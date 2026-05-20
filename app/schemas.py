from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus
    priority: int = Field(ge=1, le=5)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class Task(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int


class CurrentUser(BaseModel):
    id: int
    role: str = "user"


class HealthResponse(BaseModel):
    status: str
    env: str


class RoomUsersResponse(BaseModel):
    room_id: str
    users: list[str]
