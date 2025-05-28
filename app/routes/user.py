from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user, is_admin
from app.models.user import User
from app.schemas.user_schema import UserUpdate, UserInfoResponseForAdmin, UserInfoResponseForUser
from app.services.user_service import get_user_service, UserService

router = APIRouter()

@router.get("/me", response_model=UserInfoResponseForUser)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.put("/me", response_model=UserInfoResponseForUser)
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)
):
    return user_service.update_user_profile(db, current_user, user_update)

@router.get("/{user_id}", response_model=UserInfoResponseForAdmin)
async def get_user_info(
    user_id: int,
    _: bool = Depends(is_admin),
    user_service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)
):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
