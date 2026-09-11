import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Game, Subscription
from ..schemas import OrderIn, OrderOut
router=APIRouter(prefix="/orders",tags=["orders"])
@router.post("",response_model=OrderOut)
def create_order(payload:OrderIn,db:Session=Depends(get_db)):
    if not payload.items: raise HTTPException(400,"Cart is empty")
    rate=float(os.getenv("DEFAULT_TRY_RUB","2.28")); markup=float(os.getenv("DEFAULT_MARKUP","0.10")); total=0.0
    for item in payload.items:
        if item.quantity<1 or item.quantity>20: raise HTTPException(400,"Invalid quantity")
        model=Subscription if item.item_type=="subscription" else Game
        p=db.query(model).filter(model.id==item.item_id,model.active.is_(True)).first()
        if not p: raise HTTPException(404,f"Item {item.item_id} not found")
        if p.price_try is None: raise HTTPException(409,"Price is not available yet")
        total+=p.price_try*rate*(1+markup)*item.quantity
    oid=1000+int(total)%8999; bot=os.getenv("BOT_USERNAME","your_bot_username").lstrip('@')
    return OrderOut(id=oid,total_rub=round(total),status="awaiting_payment",bot_url=f"https://t.me/{bot}?start=order_{oid}")
