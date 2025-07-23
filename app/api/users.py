from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, EmailStr
from app.db.database import SessionLocal
from app.db.models import User, UserRole
from app.core.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

router = APIRouter()

class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    active: bool
    brewery_id: str
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    brewery_id: Optional[str] = None
    active: Optional[bool] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    brewery_id: Optional[str] = None

@router.get("/", response_model=List[UserOut])
def list_users(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.GLOBAL_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

@router.post("/", response_model=UserOut)
def create_user(data: UserCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.GLOBAL_ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    if db.query(User).filter(User.email == data.email).first():
        db.close()
        raise HTTPException(status_code=400, detail="User already exists")
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(data.password)
    user = User(
        email=data.email,
        hashed_password=hashed_password,
        role=data.role,
        active=True,
        brewery_id=data.brewery_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@router.patch("/{user_id}/deactivate")
def deactivate_user(user_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.GLOBAL_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # SEGURIDAD: Solo global_admin puede desactivar a otro global_admin
    if user.role == UserRole.GLOBAL_ADMIN and current_user.role != UserRole.GLOBAL_ADMIN:
        db.close()
        raise HTTPException(status_code=403, detail="Only global admin can deactivate global admin users")
    
    # SEGURIDAD: Un global_admin no puede desactivarse a sí mismo
    if user.id == current_user.id and current_user.role == UserRole.GLOBAL_ADMIN:
        db.close()
        raise HTTPException(status_code=403, detail="Global admin cannot deactivate themselves")
    
    setattr(user, 'active', False)
    db.commit()
    db.close()
    return {"success": True}

@router.patch("/{user_id}/activate")
def activate_user(user_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.GLOBAL_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # SEGURIDAD: Solo global_admin puede activar a otro global_admin
    if user.role == UserRole.GLOBAL_ADMIN and current_user.role != UserRole.GLOBAL_ADMIN:
        db.close()
        raise HTTPException(status_code=403, detail="Only global admin can activate global admin users")
    
    setattr(user, 'active', True)
    db.commit()
    db.close()
    return {"success": True}

@router.patch("/{user_id}")
def update_user(user_id: str, data: UserUpdate = Body(...), current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # SEGURIDAD: Solo global_admin puede modificar a otro global_admin
    if user.role == UserRole.GLOBAL_ADMIN and current_user.role != UserRole.GLOBAL_ADMIN:
        db.close()
        raise HTTPException(status_code=403, detail="Only global admin can modify global admin users")
    
    # Permisos
    if current_user.role == UserRole.GLOBAL_ADMIN:
        pass  # Puede editar cualquier campo
    elif current_user.role in [UserRole.ADMIN, UserRole.MODERATOR]:
        if user.brewery_id != current_user.brewery_id:
            db.close()
            raise HTTPException(status_code=403, detail="No puedes editar usuarios de otra cervecería")
        if data.role == UserRole.GLOBAL_ADMIN:
            db.close()
            raise HTTPException(status_code=403, detail="No puedes asignar rol de admin global")
    else:
        db.close()
        raise HTTPException(status_code=403, detail="No tienes permisos para editar usuarios")
    # Actualizar campos
    if data.email is not None:
        user.email = data.email
    if data.role is not None:
        user.role = data.role
    if data.brewery_id is not None:
        user.brewery_id = data.brewery_id
    if data.active is not None:
        user.active = data.active
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(status_code=400, detail="Integrity error")
    db.close()
    return {"success": True}

@router.delete("/{user_id}")
def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # SEGURIDAD: Solo global_admin puede eliminar a otro global_admin
    if user.role == UserRole.GLOBAL_ADMIN and current_user.role != UserRole.GLOBAL_ADMIN:
        db.close()
        raise HTTPException(status_code=403, detail="Only global admin can delete global admin users")
    
    # SEGURIDAD: Un global_admin no puede eliminarse a sí mismo
    if user.id == current_user.id and current_user.role == UserRole.GLOBAL_ADMIN:
        db.close()
        raise HTTPException(status_code=403, detail="Global admin cannot delete themselves")
    
    # Permitir solo si es global_admin o admin de la misma cervecería
    if current_user.role == UserRole.GLOBAL_ADMIN:
        pass
    elif current_user.role == UserRole.ADMIN and user.brewery_id == current_user.brewery_id:
        pass
    else:
        db.close()
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(user)
    db.commit()
    db.close()
    return {"success": True} 