from sqlalchemy.orm import Session
from .models import Game, Subscription

DEMO_GAMES = [
    {"title":"Grand Theft Auto VI","platform":"PS5","image":"https://images.unsplash.com/photo-1605901309584-818e25960a8f?auto=format&fit=crop&w=900&q=80","description":"Демо-карточка. После синхронизации каталог дополнится данными PlayStation Store Turkey.","price_try":3999,"old_price_try":None,"discount_percent":0,"store_url":"https://store.playstation.com/tr-tr/","external_id":"demo-gta-vi","featured":True},
    {"title":"EA SPORTS FC 26","platform":"PS5 / PS4","image":"https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=900&q=80","description":"Демо-карточка каталога PS4 / PS5.","price_try":2899.99,"old_price_try":None,"discount_percent":0,"store_url":"https://store.playstation.com/tr-tr/","external_id":"demo-fc26","featured":True},
    {"title":"ASTRO BOT","platform":"PS5","image":"https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=900&q=80","description":"Демо-карточка каталога PS5.","price_try":2999,"old_price_try":None,"discount_percent":0,"store_url":"https://store.playstation.com/tr-tr/","external_id":"demo-astro-bot","featured":True},
    {"title":"The Last of Us Part II","platform":"PS4","image":"https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=900&q=80","description":"Демо-карточка каталога PS4.","price_try":1399,"old_price_try":None,"discount_percent":0,"store_url":"https://store.playstation.com/tr-tr/","external_id":"demo-tlou2","featured":False},
]

FALLBACK_SUBSCRIPTIONS = [
    ("Essential",1,"PS Plus Essential — 1 месяц","PSPLUS_ESSENTIAL_1",400.0),
    ("Essential",3,"PS Plus Essential — 3 месяца","PSPLUS_ESSENTIAL_3",None),
    ("Essential",12,"PS Plus Essential — 12 месяцев","PSPLUS_ESSENTIAL_12",None),
    ("Extra",1,"PS Plus Extra — 1 месяц","PSPLUS_EXTRA_1",None),
    ("Extra",3,"PS Plus Extra — 3 месяца","PSPLUS_EXTRA_3",None),
    ("Extra",12,"PS Plus Extra — 12 месяцев","PSPLUS_EXTRA_12",None),
    ("Deluxe",1,"PS Plus Deluxe — 1 месяц","PSPLUS_DELUXE_1",None),
    ("Deluxe",3,"PS Plus Deluxe — 3 месяца","PSPLUS_DELUXE_3",None),
    ("Deluxe",12,"PS Plus Deluxe — 12 месяцев","PSPLUS_DELUXE_12",None),
]
PLUS_IMAGE="https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?auto=format&fit=crop&w=900&q=80"

def seed_catalog(db: Session):
    import os
    if db.query(Game).count()==0:
        db.add_all(Game(**x) for x in DEMO_GAMES)
    if db.query(Subscription).count()==0:
        for tier,months,title,env_name,fallback in FALLBACK_SUBSCRIPTIONS:
            db.add(Subscription(tier=tier,duration_months=months,title=title,image=PLUS_IMAGE,description="Подписка PlayStation Plus для турецкого региона.",price_try=(float(os.getenv(env_name)) if os.getenv(env_name) else fallback),store_url="https://store.playstation.com/tr-tr/pages/subscriptions/",external_id=f"fallback-{tier.lower()}-{months}",active=True))
    db.commit()
