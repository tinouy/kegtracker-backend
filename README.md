# KegTracker Backend

Backend de KegTracker: sistema de gestión de barriles y cervecerías.

## Tecnologías
- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- Docker

## Instalación local

```bash
cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus variables
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t kegtracker-backend .
docker run --env-file .env -p 8000:8000 kegtracker-backend
```

## Endpoints principales

- `/api/auth/` — Autenticación y gestión de usuarios
- `/api/kegs/` — Gestión de barriles
- `/api/breweries/` — Gestión de cervecerías
- `/api/wizard/` — Inicialización

## Migraciones

```bash
alembic upgrade head
```

## Licencia

Este software se distribuye bajo la licencia AGPL-3.0 con una cláusula adicional de no competencia.  
Ver [LICENSE](../LICENSE) para más detalles.

---

**Autor:** mperez 