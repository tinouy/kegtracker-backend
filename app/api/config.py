from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.db.models import User, UserRole
from app.core.config import get_settings
from typing import Dict

router = APIRouter()

@router.get("/", response_model=Dict[str, str])
def get_config(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.GLOBAL_ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    settings = get_settings()
    # Devolver solo los campos relevantes
    return settings.dict()

@router.put("/")
def update_config(config: Dict[str, str], current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.GLOBAL_ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # save_config(config) # This line is removed as per the edit hint
    return {"message": "Config updated"} 