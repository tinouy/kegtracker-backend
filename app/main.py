from fastapi import FastAPI
from app.core.config import get_settings
from app.api import wizard, auth, invite, users, breweries, kegs
from app.api import config as config_api
from app.db.init_db import init_db

app = FastAPI(title="KegTracker Backend")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(wizard.router, prefix="/api/wizard")  # Endpoint de inicialización: solo disponible si la app no tiene cervecerías ni usuarios
app.include_router(auth.router, prefix="/api/auth")
app.include_router(invite.router, prefix="/api/invite")
app.include_router(users.router, prefix="/api/users")
app.include_router(breweries.router, prefix="/api/breweries")
app.include_router(kegs.router, prefix="/api/kegs")
app.include_router(config_api.router, prefix="/api/config")

@app.get("/ping")
def ping():
    return {"message": "pong"} 