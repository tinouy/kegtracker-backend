# Requiere pytest, pytest-asyncio y httpx instalados
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_keg_crud():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Crear barril
        keg_data = {
            "name": "Barril Test",
            "type": "keg",
            "connector": "S",
            "capacity": 20,
            "current_content": 10,
            "beer_type": "IPA",
            "state": "ready",
            "brewery_id": 1
        }
        # Suponiendo autenticación mockeada o bypass para test
        response = await ac.post("/api/kegs/", json=keg_data)
        assert response.status_code == 200
        keg = response.json()
        keg_id = keg["id"]
        # Listar barriles
        response = await ac.get("/api/kegs/")
        assert response.status_code == 200
        # Actualizar barril
        keg_data["state"] = "in_use"
        response = await ac.patch(f"/api/kegs/{keg_id}", json=keg_data)
        assert response.status_code == 200
        # Historial
        response = await ac.get(f"/api/kegs/{keg_id}/history")
        assert response.status_code == 200
        # Eliminar barril
        response = await ac.delete(f"/api/kegs/{keg_id}")
        assert response.status_code == 200 