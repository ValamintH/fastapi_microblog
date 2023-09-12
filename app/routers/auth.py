from datetime import timedelta

from config import ACCESS_TOKEN_EXPIRE_MINUTES
from db import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas import TokenSchema
from security import authenticate_user, create_access_token
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth")


@router.post("", response_model=TokenSchema)
async def auth(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = await authenticate_user(
        username=login_data.username, password=login_data.password, db=db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return TokenSchema(access_token=access_token, token_type="bearer")
