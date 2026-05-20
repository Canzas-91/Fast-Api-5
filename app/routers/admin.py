from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_current_user, get_storage
from app.schemas import CurrentUser
from app.storage import InMemoryTaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/stats")
def get_stats(
    _: CurrentUser = Depends(require_admin),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> dict:
    return storage.stats()


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_task(
    task_id: int,
    _: CurrentUser = Depends(require_admin),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> Response:
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
