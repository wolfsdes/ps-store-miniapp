import os
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Game
from ..schemas import GameOut
router=APIRouter(prefix="/games",tags=["games"])
def settings(): return float(os.getenv("DEFAULT_TRY_RUB","2.28")),float(os.getenv("DEFAULT_MARKUP","0.10"))
def game_out(g):
    rate,markup=settings()
    return GameOut(id=g.id,title=g.title,platform=g.platform,image=g.image,description=g.description,price_try=g.price_try,old_price_try=g.old_price_try,discount_percent=g.discount_percent or 0,price_rub=round(g.price_try*rate*(1+markup)),old_price_rub=round(g.old_price_try*rate*(1+markup)) if g.old_price_try else None,store_url=g.store_url or "",featured=bool(g.featured))
@router.get("",response_model=list[GameOut])
def list_games(search:str=Query("",max_length=100),platform:str=Query("all"),discounted:bool=Query(False),db:Session=Depends(get_db)):
    q=db.query(Game).filter(Game.active.is_(True))
    if search:q=q.filter(Game.title.ilike(f"%{search}%"))
    if platform in {"PS5","PS4"}:q=q.filter(Game.platform.ilike(f"%{platform}%"))
    if discounted:q=q.filter(Game.discount_percent>0)
    return [game_out(g) for g in q.order_by(Game.featured.desc(),Game.discount_percent.desc(),Game.title.asc()).all()]
@router.get("/{game_id}",response_model=GameOut)
def get_game(game_id:int,db:Session=Depends(get_db)):
    from fastapi import HTTPException
    g=db.query(Game).filter(Game.id==game_id,Game.active.is_(True)).first()
    if not g:raise HTTPException(404,"Game not found")
    return game_out(g)
