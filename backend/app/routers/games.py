import os
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Game
from ..schemas import GameOut

router = APIRouter(prefix="/games", tags=["games"])

def settings():
    return (
        float(os.getenv("DEFAULT_TRY_RUB", "2.28")),
        float(os.getenv("DEFAULT_MARKUP", "0.10")),
    )

@router.get("", response_model=list[GameOut])
def list_games(
    search: str = Query("", max_length=100),
    platform: str = Query("all"),
    db: Session = Depends(get_db),
):
    try_rub, markup = settings()
    q = db.query(Game).filter(Game.active.is_(True))

    if search:
        q = q.filter(Game.title.ilike(f"%{search}%"))
    if platform in {"PS5", "PS4"}:
        q = q.filter(Game.platform.ilike(f"%{platform}%"))

    games = q.order_by(Game.featured.desc(), Game.title.asc()).all()

    return [
        GameOut(
            id=g.id,
            title=g.title,
            platform=g.platform,
            image=g.image,
            description=g.description,
            price_try=g.price_try,
            price_rub=round(g.price_try * try_rub * (1 + markup)),
        )
        for g in games
    ]

@router.get("/{game_id}", response_model=GameOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    try_rub, markup = settings()
    g = db.query(Game).filter(Game.id == game_id, Game.active.is_(True)).first()
    if not g:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Game not found")

    return GameOut(
        id=g.id,
        title=g.title,
        platform=g.platform,
        image=g.image,
        description=g.description,
        price_try=g.price_try,
        price_rub=round(g.price_try * try_rub * (1 + markup)),
    )
