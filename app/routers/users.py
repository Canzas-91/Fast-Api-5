from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.schemas import CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user


@router.get("/{user_id}", response_model=CurrentUser)
def get_user(user_id: int, current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    role = current_user.role if user_id == current_user.id else "user"
    return CurrentUser(id=user_id, role=role)
