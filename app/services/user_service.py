from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.schemas.user_schema import UserUpdate

class UserService:
    def update_user_profile(self, db: Session, user: User, user_update: UserUpdate) -> User:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

user_service = UserService()

def get_user_service():
    return user_service