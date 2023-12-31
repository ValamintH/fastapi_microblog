from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from config import ALGORITHM, SECRET_KEY
from dependencies.db import get_db
from fastapi import Depends, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from queries import get_user_by_email, get_user_by_name
from sqlalchemy.orm import Session


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={
                "tokenUrl": tokenUrl,
                "scopes": scopes,
            }
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="auth")


def create_access_token(
    data: dict,
    expires_delta: Union[timedelta, None] = None,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = await get_user_by_name(username=username, db=db)
    if user is None:
        return None
    return user


async def authenticate_user(username: str, password: str, db: Session):
    user = await get_user_by_name(username=username, db=db)
    if not user:
        return False
    if not user.check_password(password):
        return False
    return user


async def is_existing_username(username: str, db: Session):
    user = await get_user_by_name(username=username, db=db)
    if not user:
        return False
    return True


async def is_existing_email(email: str, db: Session):
    user = await get_user_by_email(email=email, db=db)
    if not user:
        return False
    return True
