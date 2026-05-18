from fastapi.testclient import TestClient


def test_list_users_as_admin(client: TestClient, admin_headers: dict):
    response = client.get("/users/", headers=admin_headers)
    assert response.status_code == 200


def test_list_users_as_user(client: TestClient, auth_headers: dict):
    response = client.get("/users/", headers=auth_headers)
    assert response.status_code == 403


def test_list_users_without_auth(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 401


def test_get_me(client: TestClient, auth_headers: dict):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_update_me(client: TestClient, auth_headers: dict):
    response = client.patch(
        "/users/me",
        json={"email": "updated@example.com"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


def test_update_me_cannot_change_role(client: TestClient, auth_headers: dict):
    response = client.patch(
        "/users/me",
        json={"role": "admin"},
        headers=auth_headers,
    )
    assert response.status_code == 403
