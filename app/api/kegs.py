from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.db.database import SessionLocal
from app.db.models import Keg, KegType, KegConnector, KegState, User, UserRole, KegStateHistory, Brewery
from app.core.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

router = APIRouter()

class KegOut(BaseModel):
    id: str
    name: str
    type: KegType
    connector: KegConnector
    capacity: int
    current_content: int
    beer_type: str
    state: KegState
    brewery_id: str
    brewery_name: Optional[str] = None
    location: Optional[str] = None
    user_email: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True

class KegCreate(BaseModel):
    name: str
    type: KegType
    connector: KegConnector
    capacity: int
    current_content: int
    beer_type: str
    state: KegState = KegState.READY
    brewery_id: str
    location: Optional[str] = None

@router.get("/", response_model=List[KegOut])
def list_kegs(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(10, ge=1, le=100),
    brewery_id: Optional[str] = None,  # UUID como string
    state: Optional[KegState] = None
):
    db = SessionLocal()
    query = db.query(Keg).join(Brewery, Keg.brewery_id == Brewery.id)
    if brewery_id:
        query = query.filter(Keg.brewery_id == brewery_id)
    if state:
        query = query.filter(Keg.state == state)
    kegs = query.offset(skip).limit(limit).all()
    
    # Crear respuesta con brewery_name
    result = []
    for keg in kegs:
        keg_dict = {
            "id": keg.id,
            "name": keg.name,
            "type": keg.type,
            "connector": keg.connector,
            "capacity": keg.capacity,
            "current_content": keg.current_content,
            "beer_type": keg.beer_type,
            "state": keg.state,
            "brewery_id": keg.brewery_id,
            "brewery_name": keg.brewery.name if keg.brewery else None,
            "location": keg.location,
            "user_email": None
        }
        result.append(keg_dict)
    
    db.close()
    return result

@router.post("/", response_model=KegOut)
def create_keg(data: KegCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.GLOBAL_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    keg = Keg(**data.dict())
    db.add(keg)
    try:
        db.commit()
        db.refresh(keg)
        
        # Obtener brewery_name para la respuesta
        brewery = db.query(Brewery).filter(Brewery.id == keg.brewery_id).first()
        keg_response = {
            "id": keg.id,
            "name": keg.name,
            "type": keg.type,
            "connector": keg.connector,
            "capacity": keg.capacity,
            "current_content": keg.current_content,
            "beer_type": keg.beer_type,
            "state": keg.state,
            "brewery_id": keg.brewery_id,
            "brewery_name": brewery.name if brewery else None,
            "location": keg.location,
            "user_email": None
        }
        
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(status_code=400, detail="Keg already exists")
    db.close()
    return keg_response

@router.patch("/{keg_id}", response_model=KegOut)
def update_keg(keg_id: str, data: KegCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    keg = db.query(Keg).filter(Keg.id == keg_id).first()
    if keg is None:
        db.close()
        raise HTTPException(status_code=404, detail="Keg not found")
    # Permitir editar a global_admin, admin, moderator, y usuario común solo si es de su cervecería
    if current_user.role == UserRole.USER and keg.brewery_id != current_user.brewery_id:
        db.close()
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este barril")
    old_state = keg.state
    for key, value in data.dict().items():
        setattr(keg, key, value)
    db.commit()
    db.refresh(keg)
    # Registrar historial si cambió el estado
    if old_state != keg.state:
        history = KegStateHistory(
            keg_id=keg.id,
            old_state=old_state,
            new_state=keg.state,
            user_id=current_user.id
        )
        db.add(history)
        db.commit()
    
    # Obtener brewery_name para la respuesta
    brewery = db.query(Brewery).filter(Brewery.id == keg.brewery_id).first()
    keg_response = {
        "id": keg.id,
        "name": keg.name,
        "type": keg.type,
        "connector": keg.connector,
        "capacity": keg.capacity,
        "current_content": keg.current_content,
        "beer_type": keg.beer_type,
        "state": keg.state,
        "brewery_id": keg.brewery_id,
        "brewery_name": brewery.name if brewery else None,
        "location": keg.location,
        "user_email": None
    }
    
    db.close()
    return keg_response

@router.get("/{keg_id}/history")
def get_keg_history(keg_id: str, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    history = db.query(KegStateHistory).filter(KegStateHistory.keg_id == keg_id).order_by(KegStateHistory.changed_at.desc()).all()
    # Obtener emails de los usuarios
    user_ids = list({h.user_id for h in history if h.user_id})
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u.email for u in users}
    db.close()
    return [
        {
            "old_state": h.old_state,
            "new_state": h.new_state,
            "changed_at": h.changed_at,
            "user_email": user_map.get(h.user_id) if h.user_id else None
        } for h in history
    ]

@router.delete("/{keg_id}")
def delete_keg(keg_id: str, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    keg = db.query(Keg).filter(Keg.id == keg_id).first()
    if keg is None:
        db.close()
        raise HTTPException(status_code=404, detail="Keg not found")
    db.delete(keg)
    db.commit()
    db.close()
    return {"success": True}

@router.get("/{keg_id}", response_model=KegOut)
def get_keg(keg_id: str, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    keg = db.query(Keg).join(Brewery, Keg.brewery_id == Brewery.id).filter(Keg.id == keg_id).first()
    if not keg:
        db.close()
        raise HTTPException(status_code=404, detail="Keg not found")
    if current_user.role == UserRole.USER and keg.brewery_id != current_user.brewery_id:
        db.close()
        raise HTTPException(status_code=403, detail="No tienes acceso a este barril")
    
    # Obtener email del usuario asignado si existe
    user_email = None
    if hasattr(keg, 'user_id') and keg.user_id:
        user = db.query(User).filter(User.id == keg.user_id).first()
        if user:
            user_email = user.email
    
    keg_response = {
        "id": keg.id,
        "name": keg.name,
        "type": keg.type,
        "connector": keg.connector,
        "capacity": keg.capacity,
        "current_content": keg.current_content,
        "beer_type": keg.beer_type,
        "state": keg.state,
        "brewery_id": keg.brewery_id,
        "brewery_name": keg.brewery.name if keg.brewery else None,
        "location": keg.location,
        "user_email": user_email
    }
    
    db.close()
    return keg_response 