import os
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.ps_store import sync_games, sync_subscriptions
router=APIRouter(prefix="/catalog-sync",tags=["catalog-sync"])
def auth(token):
    expected=os.getenv("ADMIN_SYNC_TOKEN","")
    if not expected: raise HTTPException(503,"ADMIN_SYNC_TOKEN is not configured")
    if token!=expected: raise HTTPException(401,"Invalid admin token")
@router.post("")
def sync_catalog(max_pages:int=Query(4,ge=1,le=50),x_admin_token:str|None=Header(default=None),db:Session=Depends(get_db)):
    auth(x_admin_token)
    return {"ok":True,"games":sync_games(db,max_pages),"subscriptions":sync_subscriptions(db)}
