import pytest
from httpx import AsyncClient
from main import app
from database import get_session
from crud import file_crud
from models import File
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock
from io import BytesIO

# 1. Función para sobrescribir la dependencia de la sesión (MOCK)
async def override_get_session():
    # En un entorno real, usarías una base de datos de prueba, pero para un test simple
    # podemos simular el comportamiento de la sesión.
    async with AsyncSession(bind=engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.mark.asyncio
async def test_create_file_success():
    # Simulamos el contenido binario de un PDF
    file_content = b"%PDF-1.4\n...cuerpo del pdf..."
    test_title = "Mi Documento de Prueba"
    test_user_id = 1 # Asumimos que el usuario 1 existe o se mockea su existencia

    # Mockear la función CRUD para simular la creación exitosa
    file_crud.create_file = MagicMock(return_value=File(
        id=1, 
        title=test_title, 
        user_id=test_user_id, 
        file=file_content[:10] # Solo guardamos una parte para el mock de retorno
    ))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/files/",
            params={"title": test_title, "user_id": test_user_id},
            # Subir el archivo como 'multipart/form-data'
            files={"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_title
    assert data["user_id"] == test_user_id
    # En un test real, verificarías la longitud del campo 'file' si es un string base64 o similar.
    print("Test de subida de archivo exitoso.")