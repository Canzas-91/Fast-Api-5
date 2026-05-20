from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException, status

from app.schemas import CurrentUser
from app.storage import task_storage


def get_current_user(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_user_role: str = Header(default="user", alias="X-User-Role"),
) -> CurrentUser:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    try:
        user_id = int(x_user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-User-Id header",
        ) from exc

    return CurrentUser(id=user_id, role=x_user_role)


def get_storage():
    return task_storage
