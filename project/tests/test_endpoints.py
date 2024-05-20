from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from app.api.endpoints.users import find_user_by_username

client = TestClient(app)

def test_create_user():
    response = client.post("/auth/register/", json={"username": "test_user", "password": "password123"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert "username" in response.json()
    assert response.json()["username"] == "test_user"

def test_login():
    with patch("app.api.endpoints.users.find_user_by_username") as mock_find_user:
        mock_find_user.return_value = {"username": "test_user", "password": "password123"}

        response = client.post("/auth/login/", json={"username": "test_user", "password": "password123"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["access_token"]

def test_task_create():
    with patch("app.api.endpoints.users.find_user_by_username") as mock_find_user:
        mock_find_user.return_value = {"username": "test_user", "password": "password123"}

        response = client.post("/auth/login/", json={"username": "test_user", "password": "password123"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["access_token"]
        access_token = response.json()["access_token"]
        response = client.post("/create", json={"description": "Описание", "completed": "false"}, headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        assert response.json() == {"description": "Описание", "completed": "false"}
        assert "id" in response.json()
        assert "created_at" in response.json()
        assert "owner_id" in response.json()

def test_task_create():
    with patch("app.api.endpoints.users.find_user_by_username") as mock_find_user:
        mock_find_user.return_value = {"username": "test_user", "password": "password123"}

        login_response = client.post("/auth/login/", json={"username": "test_user", "password": "password123"})
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
        access_token = login_response.json()["access_token"]

        create_task_response = client.post("/create", json={"description": "Описание", "completed": "false"}, headers={"Authorization": f"Bearer {access_token}"})
        assert create_task_response.status_code == 200
        
        assert "description" in create_task_response.json()
        assert "completed" in create_task_response.json()
        assert "id" in create_task_response.json()
        assert "created_at" in create_task_response.json()