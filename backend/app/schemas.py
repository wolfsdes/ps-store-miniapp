from pydantic import BaseModel

class GameOut(BaseModel):
    id: int
    title: str
    platform: str
    image: str
    description: str
    price_try: float
    price_rub: float

    class Config:
        from_attributes = True

class SettingsOut(BaseModel):
    try_rub: float
    markup: float

class OrderItemIn(BaseModel):
    game_id: int
    quantity: int = 1

class OrderIn(BaseModel):
    telegram_user_id: str
    items: list[OrderItemIn]

class OrderOut(BaseModel):
    id: int
    total_rub: float
    status: str
    bot_url: str
