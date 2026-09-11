import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Game
from ..schemas import OrderIn, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderOut)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    try_rub = float(os.getenv("DEFAULT_TRY_RUB", "2.28"))
    markup = float(os.getenv("DEFAULT_MARKUP", "0.10"))
    total = 0

    for item in payload.items:
        if item.quantity < 1 or item.quantity > 20:
            raise HTTPException(status_code=400, detail="Invalid quantity")
        game = db.query(Game).filter(Game.id == item.game_id, Game.active.is_(True)).first()
        if not game:
            raise HTTPException(status_code=404, detail=f"Game {item.game_id} not found")
        total += game.price_try * try_rub * (1 + markup) * item.quantity

    # Payment is intentionally not finalized in this MVP.
    # In production the order must be persisted and paid only after provider confirmation.
    order_id = 1000 + int(total) % 8999
    bot_username = os.getenv("BOT_USERNAME", "your_bot_username").lstrip("@")
    bot_url = f"https://t.me/{bot_username}?start=order_{order_id}"

    return OrderOut(
        id=order_id,
        total_rub=round(total),
        status="awaiting_payment",
        bot_url=bot_url,
    )
