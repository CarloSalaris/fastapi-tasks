from fastapi.testclient import TestClient


def test_create_task(client: TestClient, auth_headers: dict):
    response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "A test"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["completed"] is False


def test_create_task_without_auth(client: TestClient):
    response = client.post(
        "/tasks/",
        json={"title": "Test task"},
    )
    assert response.status_code == 401


def test_list_tasks(client: TestClient, auth_headers: dict):
    client.post("/tasks/", json={"title": "Task 1"}, headers=auth_headers)
    client.post("/tasks/", json={"title": "Task 2"}, headers=auth_headers)

    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task(client: TestClient, auth_headers: dict):
    create = client.post("/tasks/", json={"title": "Find me"}, headers=auth_headers)
    task_id = create.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


def test_get_task_not_found(client: TestClient, auth_headers: dict):
    response = client.get("/tasks/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_task(client: TestClient, auth_headers: dict):
    create = client.post("/tasks/", json={"title": "Old title"}, headers=auth_headers)
    task_id = create.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "New title", "completed": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["completed"] is True


def test_delete_task(client: TestClient, auth_headers: dict):
    create = client.post("/tasks/", json={"title": "Delete me"}, headers=auth_headers)
    task_id = create.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404
