from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from app.db.database import SessionLocal
from app.db.models import User, Brewery
from passlib.context import CryptContext
from jose import jwt
from app.core.config import get_settings
from app.services.email_service import send_email
import os
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    brewery = None
    if user and user.brewery_id:
        brewery = db.query(Brewery).filter(Brewery.id == user.brewery_id).first()
    db.close()
    if not user or not pwd_context.verify(data.password, getattr(user, 'hashed_password', '')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,  # Incluir el rol en el JWT
        "brewery_id": user.brewery_id,
        "brewery_name": brewery.name if brewery else None
    }, settings.SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    db.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from datetime import datetime, timedelta, timezone
    exp = datetime.now(timezone.utc) + timedelta(minutes=60)
    reset_token = jwt.encode({"user_id": user.id, "exp": exp.timestamp()}, settings.SECRET_KEY, algorithm="HS256")
    reset_link = f"{settings.FRONTEND_FQDN}/reset-password?token={reset_token}"
    await send_email(
        to=str(user.email),
        subject="Recupera tu contraseña",
        template_name="reset_password.html",
        context={"reset_link": reset_link, "user": user}
    )
    return {"message": "reset email sent"}

used_reset_tokens = set()

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    if data.token in used_reset_tokens:
        raise HTTPException(status_code=400, detail="Reset link already used")
    try:
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        exp = payload.get("exp")
        if exp:
            now = datetime.now(timezone.utc).timestamp()
            if now > exp:
                raise HTTPException(status_code=400, detail="Reset link expired")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = pwd_context.hash(data.password)
    db.commit()
    db.close()
    used_reset_tokens.add(data.token)
    return {"message": "password reset ok"}

@router.get("/reset-password/validate")
def validate_reset_token(token: str = Query(...)):
    if token in used_reset_tokens:
        raise HTTPException(status_code=400, detail="Reset link already used")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).timestamp()
            if now > exp:
                raise HTTPException(status_code=400, detail="Reset link expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"valid": True}

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
def change_password(data: ChangePasswordRequest, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not pwd_context.verify(data.current_password, user.hashed_password):
        db.close()
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    user.hashed_password = pwd_context.hash(data.new_password)
    db.commit()
    db.close()
    return {"message": "Contraseña cambiada correctamente"} 