from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from app.db.database import SessionLocal
from app.db.models import User, Brewery, UserRole
from app.core.config import get_settings
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.exc import IntegrityError
import datetime
from app.services.email_service import send_invite_email
import asyncio
from datetime import datetime, timezone

router = APIRouter()
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
used_invite_tokens = set()

class InviteRequest(BaseModel):
    email: EmailStr
    brewery_id: str
    role: UserRole = UserRole.USER
    expires_in_minutes: int = 60

class RegisterRequest(BaseModel):
    token: str
    password: str

@router.post("/generate")
async def generate_invite(data: InviteRequest):
    db = SessionLocal()
    brewery = db.query(Brewery).filter(Brewery.id == data.brewery_id).first()
    db.close()
    if not brewery:
        raise HTTPException(status_code=404, detail="Brewery not found")
    import datetime
    from datetime import timezone
    exp = datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=60)
    payload = {
        "email": data.email,
        "brewery_id": data.brewery_id,
        "role": data.role.value,
        "exp": exp.timestamp()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    invite_link = f"{settings.FRONTEND_FQDN}/register?token={token}"
    await send_invite_email(data.email, invite_link)
    return {"invite_link": invite_link}

@router.post("/register")
def register_user(data: RegisterRequest):
    if data.token in used_invite_tokens:
        raise HTTPException(status_code=400, detail="Invite link already used")
    try:
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload["email"]
        brewery_id = payload["brewery_id"]
        role = payload["role"]
        exp = payload.get("exp")
        if exp:
            now = datetime.now(timezone.utc).timestamp()
            if now > exp:
                raise HTTPException(status_code=400, detail="Invite link expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="User already exists")
        hashed_password = pwd_context.hash(data.password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role,
            active=True,
            brewery_id=brewery_id
        )
        db.add(user)
        db.commit()
        used_invite_tokens.add(data.token)
        return {"success": True}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    finally:
        db.close()

@router.get("/validate")
def validate_invite_token(token: str = Query(...)):
    if token in used_invite_tokens:
        raise HTTPException(status_code=400, detail="Invite link already used")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).timestamp()
            if now > exp:
                raise HTTPException(status_code=400, detail="Invite link expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"valid": True} 