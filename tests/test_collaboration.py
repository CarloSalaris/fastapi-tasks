from fastapi.testclient import TestClient


# --- Project visibility ---


def test_user_sees_project_with_assigned_task(
    client: TestClient,
    auth_headers: dict,
    admin_headers: dict,
    second_user_headers: dict,
):
    """User B can see a project owned by User A if User B has a task assigned inside it."""
    # Admin creates a project owned by testuser (auth_headers)
    project = client.post(
        "/projects/", json={"name": "Shared project"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    # Get second user's id
    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    # Project owner assigns a task to second user
    client.post(
        "/tasks/",
        json={
            "title": "Task for second user",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )

    # Second user can see the project
    response = client.get("/projects/", headers=second_user_headers)
    project_ids = [p["id"] for p in response.json()]
    assert project_id in project_ids


def test_user_cannot_see_project_without_assigned_task(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    """User B cannot see a project owned by User A if User B has no tasks inside it."""
    project = client.post(
        "/projects/", json={"name": "Private project"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    response = client.get("/projects/", headers=second_user_headers)
    project_ids = [p["id"] for p in response.json()]
    assert project_id not in project_ids


def test_user_can_get_project_with_assigned_task(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    """User B can access a specific project if they have a task inside it."""
    project = client.post(
        "/projects/", json={"name": "Shared project"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    client.post(
        "/tasks/",
        json={
            "title": "Assigned task",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )

    response = client.get(f"/projects/{project_id}", headers=second_user_headers)
    assert response.status_code == 200


def test_user_cannot_get_project_without_assigned_task(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post(
        "/projects/", json={"name": "Private project"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    response = client.get(f"/projects/{project_id}", headers=second_user_headers)
    assert response.status_code == 404


# --- Project permissions ---


def test_user_cannot_modify_project_they_dont_own(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    """Even with tasks assigned, User B cannot modify User A's project."""
    project = client.post(
        "/projects/", json={"name": "Not yours"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    client.post(
        "/tasks/",
        json={"title": "Assigned", "project_id": project_id, "user_id": second_user_id},
        headers=auth_headers,
    )

    response = client.patch(
        f"/projects/{project_id}",
        json={"name": "Hijacked"},
        headers=second_user_headers,
    )
    assert response.status_code in [403, 404]


def test_user_cannot_delete_project_they_dont_own(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post(
        "/projects/", json={"name": "Not yours"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    response = client.delete(f"/projects/{project_id}", headers=second_user_headers)
    assert response.status_code in [403, 404]


# --- Task visibility ---


def test_project_owner_sees_all_tasks_in_project(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    """Project owner sees tasks assigned to other users in their project."""
    project = client.post(
        "/projects/", json={"name": "My project"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    client.post(
        "/tasks/",
        json={"title": "Owner's task", "project_id": project_id},
        headers=auth_headers,
    )
    client.post(
        "/tasks/",
        json={
            "title": "Assigned task",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )

    response = client.get("/tasks/", headers=auth_headers)
    titles = [t["title"] for t in response.json()]
    assert "Owner's task" in titles
    assert "Assigned task" in titles


def test_assigned_user_sees_only_own_tasks(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    """User B sees only tasks assigned to them, not all tasks in the project."""
    project = client.post(
        "/projects/", json={"name": "Shared project"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    client.post(
        "/tasks/",
        json={"title": "Not for you", "project_id": project_id},
        headers=auth_headers,
    )
    client.post(
        "/tasks/",
        json={"title": "For you", "project_id": project_id, "user_id": second_user_id},
        headers=auth_headers,
    )

    response = client.get("/tasks/", headers=second_user_headers)
    titles = [t["title"] for t in response.json()]
    assert "For you" in titles
    assert "Not for you" not in titles


# --- Task creation permissions ---


def test_project_owner_can_create_task_for_other_user(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post(
        "/projects/", json={"name": "My project"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    response = client.post(
        "/tasks/",
        json={"title": "Do this", "project_id": project_id, "user_id": second_user_id},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["user_id"] == second_user_id


def test_non_owner_cannot_create_task_in_others_project(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post(
        "/projects/", json={"name": "Not yours"}, headers=auth_headers
    )
    project_id = project.json()["id"]

    response = client.post(
        "/tasks/",
        json={"title": "Sneak in", "project_id": project_id},
        headers=second_user_headers,
    )
    assert response.status_code == 403


# --- Task update permissions ---


def test_assignee_can_complete_task(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post("/projects/", json={"name": "Work"}, headers=auth_headers)
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    task = client.post(
        "/tasks/",
        json={
            "title": "Finish this",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
        headers=second_user_headers,
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_assignee_cannot_reassign_task(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post("/projects/", json={"name": "Work"}, headers=auth_headers)
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    task = client.post(
        "/tasks/",
        json={
            "title": "Not yours to move",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"user_id": 999},
        headers=second_user_headers,
    )
    assert response.status_code == 403


def test_project_owner_can_reassign_task(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post("/projects/", json={"name": "Work"}, headers=auth_headers)
    project_id = project.json()["id"]

    me_owner = client.get("/users/me", headers=auth_headers)
    owner_id = me_owner.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    task = client.post(
        "/tasks/",
        json={
            "title": "Reassign me",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"user_id": owner_id},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == owner_id


# --- Task delete permissions ---


def test_assignee_can_delete_own_task(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post("/projects/", json={"name": "Work"}, headers=auth_headers)
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    task = client.post(
        "/tasks/",
        json={
            "title": "Delete me",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=second_user_headers)
    assert response.status_code == 200


def test_project_owner_can_delete_task_in_project(
    client: TestClient, auth_headers: dict, second_user_headers: dict
):
    project = client.post("/projects/", json={"name": "Work"}, headers=auth_headers)
    project_id = project.json()["id"]

    me = client.get("/users/me", headers=second_user_headers)
    second_user_id = me.json()["id"]

    task = client.post(
        "/tasks/",
        json={
            "title": "Owner deletes",
            "project_id": project_id,
            "user_id": second_user_id,
        },
        headers=auth_headers,
    )
    task_id = task.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
