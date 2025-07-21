from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DB_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 