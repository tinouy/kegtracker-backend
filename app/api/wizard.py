from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.database import SessionLocal
from app.db.models import Brewery, User, UserRole
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class InitRequest(BaseModel):
    brewery_name: str
    admin_email: EmailStr
    admin_password: str

@router.get("/status")
def status():
    db = SessionLocal()
    initialized = db.query(Brewery).count() > 0 or db.query(User).count() > 0
    db.close()
    return {"initialized": initialized}

@router.post("/initialize")
def initialize(data: InitRequest):
    db = SessionLocal()
    # Solo permitir si no hay cervecerías ni usuarios
    if db.query(Brewery).count() > 0 or db.query(User).count() > 0:
        db.close()
        raise HTTPException(status_code=403, detail="La app ya fue inicializada")
    # Crear cervecería
    brewery = Brewery(name=data.brewery_name, active=True)
    db.add(brewery)
    db.commit()
    db.refresh(brewery)
    # Crear usuario admin
    hashed_password = pwd_context.hash(data.admin_password)
    user = User(
        email=data.admin_email,
        hashed_password=hashed_password,
        role=UserRole.GLOBAL_ADMIN,
        active=True,
        brewery_id=brewery.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    brewery_id = brewery.id
    admin_email = user.email
    db.close()
    return {"success": True, "brewery_id": brewery_id, "admin_email": admin_email} 