from typing import Optional

from models.users import User
from schemas import UserInSchema
from sqlalchemy.orm import Session


async def get_user_by_name(username: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


async def create_user(user: UserInSchema, db: Session) -> Optional[User]:
    new_user = User(username=user.username, email=user.email)
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    return new_user
