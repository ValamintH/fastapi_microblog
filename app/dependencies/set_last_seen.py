from datetime import datetime

from dependencies.db import get_db
from dependencies.security import get_current_user
from fastapi import Depends
from models.users import User
from sqlalchemy.orm import Session


async def set_last_seen(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user:
        # this could be a query
        current_user.last_seen = datetime.utcnow()
        db.commit()
