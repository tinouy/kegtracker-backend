# KegTracker Backend

KegTracker Backend: keg and brewery management system.

## Technologies
- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- Docker

## Local Installation

```bash
cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your variables
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t kegtracker-backend .
docker run --env-file .env -p 8000:8000 kegtracker-backend
```

## Main Endpoints

```
- /api/auth/ — Authentication and user management
- /api/kegs/ — Keg management
- /api/breweries/ — Brewery management
- /api/wizard/ — Initialization
```

## Migrations

```bash
alembic upgrade head
```

## Licencia

This software is distributed under the AGPL-3.0 license with an additional non-compete clause.
See [LICENSE](../LICENSE) for more details.

---

**Author:** tinouy 