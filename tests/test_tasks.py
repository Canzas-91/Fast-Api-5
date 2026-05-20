def auth_headers(user_id: int = 10, role: str = "user") -> dict[str, str]:
    return {"X-User-Id": str(user_id), "X-User-Role": role}


def create_task(client, *, user_id: int = 10, **overrides):
    payload = {
        "title": "Подготовить тесты",
        "description": "Написать интеграционные тесты",
        "status": "todo",
        "priority": 4,
    }
    payload.update(overrides)
    return client.post("/tasks", json=payload, headers=auth_headers(user_id))


def test_create_task_success(client):
    response = create_task(client)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Подготовить тесты",
        "description": "Написать интеграционные тесты",
        "status": "todo",
        "priority": 4,
        "owner_id": 10,
    }


def test_create_task_short_title_returns_422(client):
    response = create_task(client, title="ab")

    assert response.status_code == 422


def test_missing_x_user_id_returns_401(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_user_sees_only_own_tasks(client):
    create_task(client, user_id=10, title="Task A")
    create_task(client, user_id=20, title="Task B")

    response = client.get("/tasks", headers=auth_headers(10))

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Task A"]


def test_tasks_can_be_filtered_by_status_and_min_priority(client):
    create_task(client, status="todo", priority=2, title="Low todo")
    create_task(client, status="done", priority=5, title="High done")
    create_task(client, status="done", priority=3, title="Mid done")

    response = client.get(
        "/tasks",
        params={"status": "done", "min_priority": 4},
        headers=auth_headers(10),
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["High done"]


def test_update_task_status_success(client):
    create_response = create_task(client)

    response = client.patch(
        f"/tasks/{create_response.json()['id']}/status",
        json={"status": "done"},
        headers=auth_headers(10),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_get_other_user_or_missing_task_returns_404(client):
    create_response = create_task(client, user_id=10)
    task_id = create_response.json()["id"]

    other_user_response = client.get(f"/tasks/{task_id}", headers=auth_headers(99))
    missing_response = client.get("/tasks/999", headers=auth_headers(10))

    assert other_user_response.status_code == 404
    assert missing_response.status_code == 404


def test_delete_task_success(client):
    create_response = create_task(client)
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers(10))
    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers(10))

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_healthcheck_returns_environment(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
