from fastapi.testclient import TestClient


def test_create_project(client: TestClient, auth_headers: dict):
    response = client.post(
        "/projects/",
        json={"name": "Work", "color": "#FF5733"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Work"
    assert data["color"] == "#FF5733"


def test_create_project_without_auth(client: TestClient):
    response = client.post("/projects/", json={"name": "Work"})
    assert response.status_code == 401


def test_list_projects(client: TestClient, auth_headers: dict):
    client.post("/projects/", json={"name": "Work"}, headers=auth_headers)
    client.post("/projects/", json={"name": "Personal"}, headers=auth_headers)

    response = client.get("/projects/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_project(client: TestClient, auth_headers: dict):
    create = client.post("/projects/", json={"name": "Find me"}, headers=auth_headers)
    project_id = create.json()["id"]

    response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Find me"


def test_update_project(client: TestClient, auth_headers: dict):
    create = client.post("/projects/", json={"name": "Old name"}, headers=auth_headers)
    project_id = create.json()["id"]

    response = client.patch(
        f"/projects/{project_id}",
        json={"name": "New name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New name"


def test_delete_project(client: TestClient, auth_headers: dict):
    create = client.post("/projects/", json={"name": "Delete me"}, headers=auth_headers)
    project_id = create.json()["id"]

    response = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 404


def test_create_task_with_project(client: TestClient, auth_headers: dict):
    project = client.post("/projects/", json={"name": "Work"}, headers=auth_headers)
    project_id = project.json()["id"]

    task = client.post(
        "/tasks/",
        json={"title": "Do something", "project_id": project_id},
        headers=auth_headers,
    )
    assert task.status_code == 201
    assert task.json()["project_id"] == project_id


def test_create_task_without_project(client: TestClient, auth_headers: dict):
    task = client.post(
        "/tasks/",
        json={"title": "Standalone task"},
        headers=auth_headers,
    )
    assert task.status_code == 201
    assert task.json()["project_id"] is None
