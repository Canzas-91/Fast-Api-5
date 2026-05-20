from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependencies import get_current_user, get_storage
from app.schemas import CurrentUser, Task, TaskCreate, TaskStatus, TaskStatusUpdate
from app.storage import InMemoryTaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> Task:
    return storage.create_task({**payload.model_dump(), "owner_id": current_user.id})


@router.get("", response_model=list[Task])
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    min_priority: Optional[int] = Query(default=None, ge=1, le=5),
    current_user: CurrentUser = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> list[Task]:
    return storage.list_tasks(
        owner_id=current_user.id,
        status=status_filter,
        min_priority=min_priority,
    )


def _get_owned_task(
    task_id: int,
    current_user: CurrentUser,
    storage: InMemoryTaskStorage,
) -> Task:
    task = storage.get_task(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> Task:
    return _get_owned_task(task_id, current_user, storage)


@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> Task:
    _get_owned_task(task_id, current_user, storage)
    updated = storage.update_status(task_id, payload.status)
    assert updated is not None
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> Response:
    _get_owned_task(task_id, current_user, storage)
    storage.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
