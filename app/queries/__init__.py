from schemas import UserInSchema
from db import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from models import User
from typing import Optional


async def get_user(username: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()
