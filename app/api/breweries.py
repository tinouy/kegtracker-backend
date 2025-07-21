from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db.database import SessionLocal
from app.db.models import Brewery, User, UserRole
from app.core.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from typing import List

router = APIRouter()

class BreweryOut(BaseModel):
    id: str
    name: str
    active: bool
    class Config:
        orm_mode = True

class BreweryCreate(BaseModel):
    name: str

@router.get("/", response_model=List[BreweryOut])
def list_breweries(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.GLOBAL_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    breweries = db.query(Brewery).all()
    db.close()
    return breweries

@router.post("/", response_model=BreweryOut)
def create_brewery(data: BreweryCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.GLOBAL_ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    brewery = Brewery(name=data.name, active=True)
    db.add(brewery)
    try:
        db.commit()
        db.refresh(brewery)
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(status_code=400, detail="Brewery already exists")
    db.close()
    return brewery

@router.patch("/{brewery_id}/deactivate")
def deactivate_brewery(brewery_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.GLOBAL_ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    brewery = db.query(Brewery).filter(Brewery.id == brewery_id).first()
    if brewery is None:
        db.close()
        raise HTTPException(status_code=404, detail="Brewery not found")
    setattr(brewery, 'active', False)
    db.commit()
    db.close()
    return {"success": True}

@router.delete("/{brewery_id}")
def delete_brewery(brewery_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.GLOBAL_ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    brewery = db.query(Brewery).filter(Brewery.id == brewery_id).first()
    if brewery is None:
        db.close()
        raise HTTPException(status_code=404, detail="Brewery not found")
    db.delete(brewery)
    db.commit()
    db.close()
    return {"success": True} 