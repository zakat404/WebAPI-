# test_main.py
import pytest
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io
from PIL import Image

@pytest.fixture(scope="module")
def test_app():
    test_engine = create_engine("sqlite:///./test.db")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield app

    Base.metadata.drop_all(bind=test_engine)

@pytest.mark.asyncio
async def test_signup(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/signup", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_token(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        await ac.post("/api/v1/auth/signup", json={"username": "testuser", "password": "testpass"})

        response = await ac.post("/api/v1/auth/token", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await ac.get("/api/v1/images/", headers=headers)
    assert response.status_code == 200
@pytest.mark.asyncio
async def test_upload_image(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/token", data={"username": "testuser", "password": "testpass"})
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}



        image_file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color='red')
        image.save(image_file, format='JPEG')
        image_file.name = 'test_image.jpg'
        image_file.seek(0)

        files = {'file': ('test_image.jpg', image_file, 'image/jpeg')}
        response = await ac.post("/api/v1/images/?name=Test Image", headers=headers, files=files)
        assert response.status_code == 201
        assert response.json()["name"] == "Test Image"
