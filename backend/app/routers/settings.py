import os
from fastapi import APIRouter
from ..schemas import SettingsOut

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=SettingsOut)
def get_settings():
    return SettingsOut(
        try_rub=float(os.getenv("DEFAULT_TRY_RUB", "2.28")),
        markup=float(os.getenv("DEFAULT_MARKUP", "0.10")),
    )
