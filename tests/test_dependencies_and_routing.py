from tests.test_tasks import auth_headers, create_task


def test_users_me_returns_current_user(client):
    response = client.get("/users/me", headers=auth_headers(10))

    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_missing_user_id_header_returns_401(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_regular_user_gets_403_on_admin_stats(client):
    response = client.get("/admin/stats", headers=auth_headers(10, role="user"))

    assert response.status_code == 403


def test_admin_gets_global_stats(client):
    create_task(client, user_id=10, status="todo", title="todo task")
    create_task(client, user_id=20, status="done", title="done task")

    response = client.get("/admin/stats", headers=auth_headers(1, role="admin"))

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 2,
        "by_status": {"todo": 1, "in_progress": 0, "done": 1},
    }


def test_regular_user_cannot_delete_foreign_task_via_tasks_route(client):
    task_id = create_task(client, user_id=10).json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers(20))

    assert response.status_code == 404


def test_admin_can_delete_foreign_task(client):
    task_id = create_task(client, user_id=10).json()["id"]

    response = client.delete(
        f"/admin/tasks/{task_id}",
        headers=auth_headers(1, role="admin"),
    )

    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=auth_headers(10)).status_code == 404


def test_openapi_groups_routes_by_tags(client):
    response = client.get("/openapi.json")
    tags_by_path = {
        "/tasks": response.json()["paths"]["/tasks"]["get"]["tags"],
        "/users/me": response.json()["paths"]["/users/me"]["get"]["tags"],
        "/admin/stats": response.json()["paths"]["/admin/stats"]["get"]["tags"],
    }

    assert tags_by_path["/tasks"] == ["tasks"]
    assert tags_by_path["/users/me"] == ["users"]
    assert tags_by_path["/admin/stats"] == ["admin"]
