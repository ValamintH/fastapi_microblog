from fastapi import Depends, status, HTTPException
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM, oauth2_scheme
from datetime import datetime, timedelta
from typing import Union
from db import get_db
from sqlalchemy.orm import Session
from queries import get_user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def authenticate_user(username: str, password: str, db: Session):
    user = await get_user(username=username, db=db)
    if not user:
        return False
    if not user.check_password(password):
        return False
    return user
