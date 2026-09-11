from pydantic import BaseModel

class GameOut(BaseModel):
    id: int
    type: str = "game"
    title: str
    platform: str
    image: str
    description: str
    price_try: float
    old_price_try: float | None = None
    discount_percent: int = 0
    price_rub: float
    old_price_rub: float | None = None
    store_url: str = ""
    featured: bool = False
    class Config:
        from_attributes = True

class SubscriptionOut(BaseModel):
    id: int
    type: str = "subscription"
    title: str
    tier: str
    duration_months: int
    image: str
    description: str
    price_try: float
    price_rub: float
    store_url: str = ""
    class Config:
        from_attributes = True

class SettingsOut(BaseModel):
    try_rub: float
    markup: float

class OrderItemIn(BaseModel):
    item_id: int
    item_type: str = "game"
    quantity: int = 1

class OrderIn(BaseModel):
    telegram_user_id: str
    items: list[OrderItemIn]

class OrderOut(BaseModel):
    id: int
    total_rub: float
    status: str
    bot_url: str
