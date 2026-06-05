import pytest
from fastapi.testclient import TestClient
from main import app
from database import Database

client = TestClient(app)

def test_get_pereval_not_found():
    """Тест: GET /submitData/{id} - перевал не найден"""
    response = client.get("/submitData/99999")
    assert response.status_code == 200
    assert response.json()["status"] == 0
    assert "не найден" in response.json()["message"]

def test_get_perevals_by_user_not_found():
    """Тест: GET /submitData/?user_email - пользователь не найден"""
    response = client.get("/submitData/?user_email=notexist@example.com")
    assert response.status_code == 200
    assert response.json()["status"] == 0

def test_create_pereval():
    """Тест: POST /submitData - создание перевала"""
    test_data = {
        "beauty_title": "Тестовый перевал",
        "title": "Pytest Mountain",
        "other_titles": "Тест",
        "connect": "",
        "add_time": "2024-01-01 12:00:00",
        "user": {
            "email": "pytest@example.com",
            "fam": "Тестов",
            "name": "Тест",
            "otc": "Тестович",
            "phone": "+7 999 999 99 99"
        },
        "coords": {
            "latitude": "55.0",
            "longitude": "37.0",
            "height": "1000"
        },
        "level": {
            "winter": "1A",
            "summer": "1A",
            "autumn": "1A",
            "spring": "1A"
        },
        "images": []
    }
    response = client.post("/submitData", json=test_data)
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["id"] is not None

def test_patch_pereval():
    """Тест: PATCH /submitData/{id} - редактирование"""
    # Сначала создаём перевал
    test_data = {
        "beauty_title": "Для редактирования",
        "title": "Edit Mountain",
        "other_titles": "",
        "connect": "",
        "add_time": "2024-01-01 12:00:00",
        "user": {
            "email": "edit@example.com",
            "fam": "Редакторов",
            "name": "Редактор",
            "otc": "",
            "phone": "+7 888 888 88 88"
        },
        "coords": {
            "latitude": "56.0",
            "longitude": "38.0",
            "height": "2000"
        },
        "level": None,
        "images": []
    }
    create_response = client.post("/submitData", json=test_data)
    pereval_id = create_response.json()["id"]
    
    # Редактируем
    patch_response = client.patch(
        f"/submitData/{pereval_id}",
        json={"title": "Новое название"}
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["state"] == 1

def test_get_pereval_by_id():
    """Тест: GET /submitData/{id} - получение после создания"""
    response = client.get("/submitData/1")
    assert response.status_code == 200
    assert "id" in response.json()