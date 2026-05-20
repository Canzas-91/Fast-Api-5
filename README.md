# Fast-Api-5

FastAPI-приложение для контрольной работы №5: задачи, зависимости, Docker и WebSocket-комнаты.

## Структура

```text
app/
tests/
Dockerfile
docker-compose.yml
requirements.txt
```

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Приложение будет доступно на `http://127.0.0.1:8000`.

## Запуск тестов

```bash
pytest
```

## Docker

```bash
docker compose up --build
```

Проверка:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

## Основные маршруты

- `GET /health`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}/status`
- `DELETE /tasks/{task_id}`
- `GET /users/me`
- `GET /users/{user_id}`
- `GET /admin/stats`
- `DELETE /admin/tasks/{task_id}`
- `GET /rooms/{room_id}/users`
- `WS /ws/rooms/{room_id}?username=alice`
