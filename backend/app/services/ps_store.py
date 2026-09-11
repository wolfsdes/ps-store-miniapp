import os, re, time
from dataclasses import dataclass
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ..models import Game, Subscription

BASE="https://store.playstation.com"
PS5_CATEGORY="4cbf39e2-5749-4970-ba81-93a489e4570c"
PS4_CATEGORY="44d8bb20-653e-431e-8ad0-c0a365f68d2f"
SUBSCRIPTIONS_URL=f"{BASE}/tr-tr/pages/subscriptions/"
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; 24XSTORE-CatalogBot/1.0; +https://24xstore.ru)","Accept-Language":"tr-TR,tr;q=0.9,en;q=0.7"}
TL_RE=re.compile(r"(?<!\d)(\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:,\d{2})?)\s*TL",re.I)
DISCOUNT_RE=re.compile(r"[-%]\s*(\d{1,2})|(\d{1,2})\s*%",re.I)
DURATION_RE=re.compile(r"(\d+)\s*(?:Aylık|Month)",re.I)

@dataclass
class ScrapedItem:
    external_id:str; title:str; url:str; image:str; price_try:float; old_price_try:float|None; discount_percent:int; platform:str

def _money(raw): return float(raw.replace('.','').replace(',','.'))
def _prices(text):
    vals=[]
    for m in TL_RE.finditer(text.replace('\xa0',' ')):
        try: vals.append(_money(m.group(1)))
        except ValueError: pass
    if not vals: return None,None
    current=vals[0]; old=max(vals) if len(vals)>1 and max(vals)>current else None
    return current,old

def _platform(text,fallback):
    p5=bool(re.search(r"\bPS5\b",text,re.I)); p4=bool(re.search(r"\bPS4\b",text,re.I))
    return "PS5 / PS4" if p5 and p4 else "PS5" if p5 else "PS4" if p4 else fallback

def _card(a):
    node=a
    for _ in range(7):
        if node is None: break
        t=' '.join(node.stripped_strings)
        if 'TL' in t and len(t)<2500: return node
        node=node.parent
    return a.parent or a

def scrape_category(category_id,platform,max_pages=3):
    out={}; s=requests.Session(); s.headers.update(HEADERS)
    for page in range(1,max_pages+1):
        r=s.get(f"{BASE}/tr-tr/category/{category_id}/{page}",timeout=25); r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
        links=[a for a in soup.find_all('a',href=True) if '/product/' in a.get('href','')]
        if not links: break
        before=len(out)
        for a in links:
            href=urljoin(BASE,a['href'].split('?')[0]); ext=href.rstrip('/').split('/')[-1]
            card=_card(a); text=' '.join(card.stripped_strings); price,old=_prices(text)
            if price is None: continue
            img=card.find('img'); image=(img.get('src') or img.get('data-src') or '') if img else ''; title=(img.get('alt') or '').strip() if img else ''
            if not title:
                candidates=[x.strip() for x in a.stripped_strings if 2<len(x.strip())<180]
                if not candidates: candidates=[x.strip() for x in card.stripped_strings if 2<len(x.strip())<180]
                title=next((x for x in candidates if 'TL' not in x and not re.fullmatch(r"[-%0-9 ]+",x)), '')
            if not title: continue
            dm=DISCOUNT_RE.search(text); disc=int(dm.group(1) or dm.group(2) or 0) if dm else (round((1-price/old)*100) if old and old>price else 0)
            out[ext]=ScrapedItem(ext,title,href,image,price,old,disc,_platform(text,platform))
        if len(out)==before: break
        time.sleep(.2)
    return list(out.values())

def sync_games(db:Session,max_pages=None):
    max_pages=max_pages or int(os.getenv('PS_STORE_MAX_PAGES','4'))
    scraped=scrape_category(PS5_CATEGORY,'PS5',max_pages)+scrape_category(PS4_CATEGORY,'PS4',max_pages)
    merged={}
    for x in scraped:
        if x.external_id in merged and merged[x.external_id].platform!=x.platform: merged[x.external_id].platform='PS5 / PS4'
        else: merged[x.external_id]=x
    created=updated=0
    for x in merged.values():
        g=db.query(Game).filter(Game.external_id==x.external_id).first()
        if not g:
            g=Game(external_id=x.external_id,title=x.title,platform=x.platform,image=x.image or 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?auto=format&fit=crop&w=900&q=80',description='Игра из PlayStation Store Turkey.',price_try=x.price_try,old_price_try=x.old_price_try,discount_percent=x.discount_percent,store_url=x.url,active=True,featured=False); db.add(g); created+=1
        else:
            g.title=x.title; g.platform=x.platform; g.image=x.image or g.image; g.price_try=x.price_try; g.old_price_try=x.old_price_try; g.discount_percent=x.discount_percent; g.store_url=x.url; g.active=True; updated+=1
    db.commit(); return {'found':len(merged),'created':created,'updated':updated,'pages_per_platform':max_pages}

def _tier(text):
    return next((x for x in ('Essential','Extra','Deluxe') if x.lower() in text.lower()),None)

def sync_subscriptions(db:Session):
    s=requests.Session(); s.headers.update(HEADERS); r=s.get(SUBSCRIPTIONS_URL,timeout=25); r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
    candidates={}
    for a in soup.find_all('a',href=True):
        href=a.get('href',''); label=' '.join(a.stripped_strings)
        if ('playstation plus' in label.lower() or 'ps plus' in label.lower()) and ('/concept/' in href or '/product/' in href): candidates[urljoin(BASE,href.split('?')[0])]=label
    candidates.setdefault(f"{BASE}/tr-tr/concept/10004507/","PlayStation Plus Essential: 1 Aylık")
    found=0
    for url,hint in list(candidates.items())[:30]:
        try:
            pr=s.get(url,timeout=25); pr.raise_for_status(); ps=BeautifulSoup(pr.text,'html.parser'); h1=ps.find('h1'); title=' '.join(h1.stripped_strings) if h1 else hint; text=' '.join(ps.stripped_strings)
            tier=_tier(title+' '+text[:1500]); dm=DURATION_RE.search(title+' '+text[:1200]); duration=int(dm.group(1)) if dm else None; price,_=_prices(text[:5000])
            if not tier or not duration or price is None: continue
            ext=url.rstrip('/').split('/')[-1]; sub=db.query(Subscription).filter(Subscription.tier==tier,Subscription.duration_months==duration).first()
            if not sub:
                sub=Subscription(tier=tier,duration_months=duration,title=f"PS Plus {tier} — {duration} мес.",image='https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?auto=format&fit=crop&w=900&q=80',description='Подписка PlayStation Plus для турецкого региона.',price_try=price,store_url=url,external_id=ext,active=True); db.add(sub)
            else:
                sub.price_try=price; sub.store_url=url; sub.external_id=ext; sub.active=True
            found+=1
        except Exception: continue
    db.commit(); return {'updated':found,'discovered_links':len(candidates)}
