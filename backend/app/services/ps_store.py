import json
import os
import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from ..models import Game, Subscription

STORE_BASE = "https://store.playstation.com"
GRAPHQL_URL = "https://web.np.playstation.com/api/graphql/v1/op"
PS5_CATEGORY = "4cbf39e2-5749-4970-ba81-93a489e4570c"
PS4_CATEGORY = "44d8bb20-653e-431e-8ad0-c0a365f68d2f"
SUBSCRIPTIONS_URL = f"{STORE_BASE}/tr-tr/pages/subscriptions/"

# Current persisted-query hash used by the public PlayStation Store catalogue.
# Sony may replace it, so it is overridable without changing the code:
# PS_STORE_QUERY_HASH=<new hash>
DEFAULT_CATEGORY_QUERY_HASH = (
    "9845afc0dbaab4965f6563fffc703f588c8e76792000e8610843b8d3ee9c4c09"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; 24XSTORE-CatalogBot/2.0; +https://24xstore.ru)",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.7",
    "x-psn-store-locale-override": "tr-tr",
    "content-type": "application/json",
}

TL_RE = re.compile(
    r"(?<!\d)(\d{1,3}(?:[.\s]\d{3})*(?:,\d{1,2})|\d+(?:,\d{1,2})?)\s*(?:TL|₺)",
    re.I,
)
DISCOUNT_RE = re.compile(r"(\d{1,2})\s*%", re.I)
DURATION_RE = re.compile(r"(\d+)\s*(?:Aylık|Ay|Month)", re.I)


@dataclass
class ScrapedItem:
    external_id: str
    title: str
    url: str
    image: str
    price_try: float
    old_price_try: float | None
    discount_percent: int
    platform: str


def _money(value):
    """Convert PlayStation price fields to a TRY float."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for key in ("value", "amount", "price", "formattedValue", "displayValue"):
            if key in value:
                parsed = _money(value[key])
                if parsed is not None:
                    return parsed
        return None

    raw = str(value).replace("\xa0", " ").strip()
    m = TL_RE.search(raw)
    number = m.group(1) if m else re.sub(r"[^0-9,.-]", "", raw)
    if not number:
        return None

    number = number.replace(" ", "")
    # Turkish price: 1.299,90. Also tolerate plain 1299.90.
    if "," in number:
        number = number.replace(".", "").replace(",", ".")
    elif number.count(".") > 1:
        number = number.replace(".", "")

    try:
        return float(number)
    except ValueError:
        return None


def _prices_from_text(text):
    vals = []
    for m in TL_RE.finditer(text.replace("\xa0", " ")):
        parsed = _money(m.group(0))
        if parsed is not None:
            vals.append(parsed)
    if not vals:
        return None, None
    current = vals[0]
    old = max(vals) if len(vals) > 1 and max(vals) > current else None
    return current, old


def _platform_from_list(platforms, fallback):
    values = {str(x).upper() for x in (platforms or [])}
    has5 = any("PS5" in x for x in values)
    has4 = any("PS4" in x for x in values)
    if has5 and has4:
        return "PS5 / PS4"
    if has5:
        return "PS5"
    if has4:
        return "PS4"
    return fallback


def _product_image(product):
    media = product.get("media") or []
    for wanted in ("MASTER", "BACKGROUND", "SCREENSHOT"):
        for item in media:
            if str(item.get("role", "")).upper() == wanted and item.get("url"):
                return item["url"]
    for item in media:
        if item.get("url"):
            return item["url"]
    return ""


def _discount_percent(price_node, current, old):
    text = str((price_node or {}).get("discountText") or "")
    m = DISCOUNT_RE.search(text)
    if m:
        return int(m.group(1))
    if old and current is not None and old > current:
        return max(0, min(99, round((1 - current / old) * 100)))
    return 0


def _graphql_page(session, category_id, offset, size=24):
    query_hash = os.getenv("PS_STORE_QUERY_HASH", DEFAULT_CATEGORY_QUERY_HASH).strip()
    variables = {
        "id": category_id,
        "pageArgs": {"size": size, "offset": offset},
        "sortBy": {"name": "productReleaseDate", "isAscending": False},
        "filterBy": [],
        "facetOptions": [],
    }
    extensions = {
        "persistedQuery": {"version": 1, "sha256Hash": query_hash}
    }

    response = session.get(
        GRAPHQL_URL,
        params={
            "operationName": "categoryGridRetrieve",
            "variables": json.dumps(variables, separators=(",", ":")),
            "extensions": json.dumps(extensions, separators=(",", ":")),
        },
        timeout=30,
    )
    response.raise_for_status()

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("PlayStation API returned non-JSON data") from exc

    if payload.get("errors"):
        msg = payload["errors"][0].get("message", "unknown GraphQL error")
        raise RuntimeError(
            "PlayStation catalogue API rejected the query: "
            f"{msg}. PS_STORE_QUERY_HASH may need updating."
        )

    grid = (payload.get("data") or {}).get("categoryGridRetrieve")
    if not isinstance(grid, dict):
        raise RuntimeError("PlayStation catalogue API returned an unexpected response")
    return grid


def fetch_category(category_id, fallback_platform, max_pages=3):
    """Read full games from the public PlayStation Store GraphQL catalogue."""
    out = {}
    session = requests.Session()
    session.headers.update(HEADERS)

    page_size = int(os.getenv("PS_STORE_PAGE_SIZE", "24"))
    page_size = max(1, min(page_size, 100))

    for page in range(max_pages):
        offset = page * page_size
        grid = _graphql_page(session, category_id, offset, page_size)
        products = grid.get("products") or []
        if not products:
            break

        for product in products:
            # This is the critical DLC/currency filter: only full games are imported.
            if str(product.get("storeDisplayClassification", "")).upper() != "FULL_GAME":
                continue

            platforms = product.get("platforms") or []
            platform = _platform_from_list(platforms, fallback_platform)
            if platform not in {"PS4", "PS5", "PS5 / PS4"}:
                continue

            price_node = product.get("price") or {}
            base_price = _money(price_node.get("basePrice"))
            discounted_price = _money(price_node.get("discountedPrice"))
            current = discounted_price if discounted_price is not None else base_price
            old = base_price if base_price and current is not None and base_price > current else None

            # Skip free/included/unavailable listings: the store needs an actual TRY price.
            if current is None or current <= 0:
                continue

            external_id = str(product.get("id") or product.get("conceptId") or "").strip()
            title = str(product.get("name") or "").strip()
            if not external_id or not title:
                continue

            out[external_id] = ScrapedItem(
                external_id=external_id,
                title=title,
                url=f"{STORE_BASE}/tr-tr/product/{external_id}",
                image=_product_image(product),
                price_try=current,
                old_price_try=old,
                discount_percent=_discount_percent(price_node, current, old),
                platform=platform,
            )

        page_info = grid.get("pageInfo") or {}
        total = page_info.get("totalCount")
        if isinstance(total, int) and offset + page_size >= total:
            break
        if len(products) < page_size:
            break
        time.sleep(0.15)

    return list(out.values())


def sync_games(db: Session, max_pages=None):
    max_pages = max_pages or int(os.getenv("PS_STORE_MAX_PAGES", "4"))
    ps5 = fetch_category(PS5_CATEGORY, "PS5", max_pages)
    ps4 = fetch_category(PS4_CATEGORY, "PS4", max_pages)

    merged = {}
    for item in ps5 + ps4:
        previous = merged.get(item.external_id)
        if previous and previous.platform != item.platform:
            previous.platform = "PS5 / PS4"
        else:
            merged[item.external_id] = item

    created = updated = 0
    placeholder = (
        "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3"
        "?auto=format&fit=crop&w=900&q=80"
    )

    for item in merged.values():
        game = db.query(Game).filter(Game.external_id == item.external_id).first()
        if not game:
            game = Game(
                external_id=item.external_id,
                title=item.title,
                platform=item.platform,
                image=item.image or placeholder,
                description="Игра из PlayStation Store Turkey.",
                price_try=item.price_try,
                old_price_try=item.old_price_try,
                discount_percent=item.discount_percent,
                store_url=item.url,
                active=True,
                featured=False,
            )
            db.add(game)
            created += 1
        else:
            game.title = item.title
            game.platform = item.platform
            game.image = item.image or game.image
            game.price_try = item.price_try
            game.old_price_try = item.old_price_try
            game.discount_percent = item.discount_percent
            game.store_url = item.url
            game.active = True
            updated += 1

    db.commit()
    return {
        "source": "playstation_graphql",
        "found": len(merged),
        "created": created,
        "updated": updated,
        "ps5_found": len(ps5),
        "ps4_found": len(ps4),
        "pages_per_platform": max_pages,
    }


def _tier(text):
    return next(
        (x for x in ("Essential", "Extra", "Deluxe") if x.lower() in text.lower()),
        None,
    )


def sync_subscriptions(db: Session):
    """Keep the existing public-page PS Plus synchroniser."""
    session = requests.Session()
    session.headers.update(HEADERS)
    response = session.get(SUBSCRIPTIONS_URL, timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    candidates = {}
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        label = " ".join(a.stripped_strings)
        if (
            "playstation plus" in label.lower() or "ps plus" in label.lower()
        ) and ("/concept/" in href or "/product/" in href):
            candidates[urljoin(STORE_BASE, href.split("?")[0])] = label

    candidates.setdefault(
        f"{STORE_BASE}/tr-tr/concept/10004507/",
        "PlayStation Plus Essential: 1 Aylık",
    )

    found = 0
    for url, hint in list(candidates.items())[:30]:
        try:
            pr = session.get(url, timeout=25)
            pr.raise_for_status()
            page = BeautifulSoup(pr.text, "html.parser")
            h1 = page.find("h1")
            title = " ".join(h1.stripped_strings) if h1 else hint
            text = " ".join(page.stripped_strings)
            tier = _tier(title + " " + text[:1500])
            dm = DURATION_RE.search(title + " " + text[:1200])
            duration = int(dm.group(1)) if dm else None
            price, _ = _prices_from_text(text[:5000])
            if not tier or not duration or price is None:
                continue

            external_id = url.rstrip("/").split("/")[-1]
            sub = (
                db.query(Subscription)
                .filter(
                    Subscription.tier == tier,
                    Subscription.duration_months == duration,
                )
                .first()
            )
            if not sub:
                sub = Subscription(
                    tier=tier,
                    duration_months=duration,
                    title=f"PS Plus {tier} — {duration} мес.",
                    image=(
                        "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3"
                        "?auto=format&fit=crop&w=900&q=80"
                    ),
                    description="Подписка PlayStation Plus для турецкого региона.",
                    price_try=price,
                    store_url=url,
                    external_id=external_id,
                    active=True,
                )
                db.add(sub)
            else:
                sub.price_try = price
                sub.store_url = url
                sub.external_id = external_id
                sub.active = True
            found += 1
        except Exception:
            continue

    db.commit()
    return {"updated": found, "discovered_links": len(candidates)}
