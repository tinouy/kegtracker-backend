from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import declarative_base, relationship
import enum
from datetime import datetime
import uuid

Base = declarative_base()

class UserRole(str, enum.Enum):
    GLOBAL_ADMIN = "global_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class Brewery(Base):
    __tablename__ = "breweries"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    active = Column(Boolean, default=True)
    users = relationship("User", back_populates="brewery")
    kegs = relationship("Keg", back_populates="brewery")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    brewery_id = Column(String, ForeignKey("breweries.id"))
    brewery = relationship("Brewery", back_populates="users")

class KegType(str, enum.Enum):
    KEG = "keg"
    CORNI = "corni"

class KegConnector(str, enum.Enum):
    S = "S"
    A = "A"
    G = "G"
    BALL_LOCK = "ball_lock"
    PIN_LOCK = "pin_lock"

class KegState(str, enum.Enum):
    IN_USE = "in_use"
    EMPTY = "empty"
    DIRTY = "dirty"
    CLEAN = "clean"
    READY = "ready"

class Keg(Base):
    __tablename__ = "kegs"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    type = Column(Enum(KegType))
    connector = Column(Enum(KegConnector))
    capacity = Column(Integer)
    current_content = Column(Integer)
    beer_type = Column(String)
    state = Column(Enum(KegState), default=KegState.READY)
    brewery_id = Column(String, ForeignKey("breweries.id"))
    brewery = relationship("Brewery", back_populates="kegs")
    location = Column(String, nullable=True)

class KegStateHistory(Base):
    __tablename__ = "keg_state_history"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    keg_id = Column(String, ForeignKey("kegs.id"))
    old_state = Column(Enum(KegState))
    new_state = Column(Enum(KegState))
    changed_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    keg = relationship("Keg", backref="state_history")
    user = relationship("User") 