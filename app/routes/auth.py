from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, Token, User as UserSchema, PasswordResetRequest
from app.core.security import get_current_user, is_admin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

@router.post("/register", response_model=UserSchema)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The email has already been registered"
        )
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The username has already been registered"
        )
    
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# @router.post("adminRegister", response_model=UserSchema)
# def admin_register(user_in: UserCreate, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == user_in.email).first()
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The email has already been registered"
#         )
#     user = db.query(User).filter(User.username == user_in.username).first()
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The username has already been registered"
#         )
    
#     user = User(
#         username=user_in.username,
#         email=user_in.email,
#         hashed_password=get_password_hash(user_in.password),
#         full_name=user_in.full_name,
#         phone=user_in.phone,
#         role="admin",
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user

# admin reset user password
@router.post("/reset-user-password")
def reset_user_password(
    user_email: str,
    new_password: str,
    _: bool = Depends(is_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Password reset successfully"}

@router.post("/reset-password")
def reset_password(
    password_reset_request: PasswordResetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password_reset_request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if len(password_reset_request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    current_user.hashed_password = get_password_hash(password_reset_request.new_password)
    db.commit()
    return {"message": "Password reset successfully"}

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == form_data.username,
                User.email == form_data.username
            )
        )
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The username or password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires, role=user.role
    )
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
        }