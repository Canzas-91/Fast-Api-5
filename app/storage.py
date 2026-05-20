from __future__ import annotations

from collections import Counter
from threading import Lock

from fastapi import WebSocket

from app.schemas import Task, TaskStatus


class InMemoryTaskStorage:
    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._tasks: dict[int, Task] = {}
            self._next_id = 1

    def create_task(self, data: dict) -> Task:
        with self._lock:
            task = Task(id=self._next_id, **data)
            self._tasks[self._next_id] = task
            self._next_id += 1
            return task

    def list_tasks(
        self,
        owner_id: int,
        status: TaskStatus | None = None,
        min_priority: int | None = None,
    ) -> list[Task]:
        tasks = [
            task
            for task in self._tasks.values()
            if task.owner_id == owner_id
            and (status is None or task.status == status)
            and (min_priority is None or task.priority >= min_priority)
        ]
        return sorted(tasks, key=lambda task: task.id)

    def get_task(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def update_status(self, task_id: int, status: TaskStatus) -> Task | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            updated = task.model_copy(update={"status": status})
            self._tasks[task_id] = updated
            return updated

    def delete_task(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def stats(self) -> dict:
        counter = Counter(task.status.value for task in self._tasks.values())
        return {
            "total_tasks": len(self._tasks),
            "by_status": {
                "todo": counter.get("todo", 0),
                "in_progress": counter.get("in_progress", 0),
                "done": counter.get("done", 0),
            },
        }


class RoomManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self._rooms: dict[str, list[tuple[str, WebSocket]]] = {}

    def reset(self) -> None:
        with self._lock:
            self._rooms = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        with self._lock:
            room = self._rooms.setdefault(room_id, [])
            room.append((username, websocket))

    async def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        with self._lock:
            room = self._rooms.get(room_id, [])
            filtered = [
                (existing_username, existing_websocket)
                for existing_username, existing_websocket in room
                if not (
                    existing_username == username and existing_websocket is websocket
                )
            ]
            if filtered:
                self._rooms[room_id] = filtered
            else:
                self._rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, payload: dict) -> None:
        with self._lock:
            connections = [websocket for _, websocket in self._rooms.get(room_id, [])]
        for websocket in connections:
            await websocket.send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        with self._lock:
            users = [username for username, _ in self._rooms.get(room_id, [])]
        return sorted(users)


task_storage = InMemoryTaskStorage()
room_manager = RoomManager()
