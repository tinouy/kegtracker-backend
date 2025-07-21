import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# No importar get_settings de sí mismo aquí, para evitar import circular

def get_settings():
    class Settings(BaseSettings):
        DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite")
        DB_URL: str = os.getenv("DB_URL", "sqlite:///./kegtracker.db")
        SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
        SMTP_PORT: int = int(os.getenv("SMTP_PORT", 25))
        SMTP_USER: str = os.getenv("SMTP_USER", "")
        SMTP_PASS: str = os.getenv("SMTP_PASS", "")
        SMTP_FROM: str = os.getenv("SMTP_FROM", "")
        SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
        DEBUG: bool = True
        BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
        BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
        FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "0.0.0.0")
        FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", 8080))
        FRONTEND_FQDN: str = os.getenv("FRONTEND_FQDN", "http://localhost:8080")
        class Config:
            env_file = ".env"
    return Settings() 