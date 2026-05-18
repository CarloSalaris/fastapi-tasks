from fastapi.testclient import TestClient


def test_register(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "email": "new@example.com", "password": "pass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data


def test_register_first_user_is_admin(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"username": "first", "email": "first@example.com", "password": "pass123"},
    )
    assert response.json()["role"] == "admin"


def test_register_duplicate_email(client: TestClient):
    client.post(
        "/auth/register",
        json={"username": "user1", "email": "same@example.com", "password": "pass123"},
    )
    response = client.post(
        "/auth/register",
        json={"username": "user2", "email": "same@example.com", "password": "pass456"},
    )
    assert response.status_code == 409


def test_login(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "pass123",
        },
    )
    response = client.post(
        "/auth/token",
        data={"username": "loginuser", "password": "pass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "pass123",
        },
    )
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpass"},
    )
    assert response.status_code == 401
