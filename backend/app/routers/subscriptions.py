import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Subscription
from ..schemas import SubscriptionOut
router=APIRouter(prefix="/subscriptions",tags=["subscriptions"])
@router.get("",response_model=list[SubscriptionOut])
def list_subscriptions(db:Session=Depends(get_db)):
    rate=float(os.getenv("DEFAULT_TRY_RUB","2.28")); markup=float(os.getenv("DEFAULT_MARKUP","0.10"))
    items=db.query(Subscription).filter(Subscription.active.is_(True)).order_by(Subscription.tier.asc(),Subscription.duration_months.asc()).all()
    return [SubscriptionOut(id=x.id,title=x.title,tier=x.tier,duration_months=x.duration_months,image=x.image,description=x.description,price_try=x.price_try,price_rub=round(x.price_try*rate*(1+markup)) if x.price_try is not None else None,store_url=x.store_url or "") for x in items]
