from fastapi import Request, Depends, APIRouter, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRoute
from forms import LoginForm
from flash import templates, Flash
from models import User
from db import get_db
from security import get_current_user
from sqlalchemy.orm import Session
from schemas import UserInSchema
from typing import Callable
import httpx


class ContextIncludedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # authorization: str = request.cookies.get("access_token")
            # print("access_token is", authorization)

            new_headers = request.headers.mutablecopy() # старый функционал через хэдерс
            new_headers.append(
                "authorization",
                f"Bearer {request.session['access_token']}"
            )
            request._headers = new_headers
            request.scope.update(headers=request.headers.raw)

            response: Response = await original_route_handler(request)
            return response

        return custom_route_handler


router = APIRouter(route_class=ContextIncludedRoute)


@router.get("/", response_class=HTMLResponse)
@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return templates.TemplateResponse("home.html", {"request": request, "user": user, "posts": posts})


@router.get("/login", response_class=HTMLResponse)
@router.post("/login", response_class=RedirectResponse)
async def login(request: Request, response: Response):
    form = await LoginForm.from_formdata(request)
    if await form.validate_on_submit():
        form_data = {"username": form.username.data, "password": form.password.data}

        async with httpx.AsyncClient() as client:
            token_response = await client.post(str(request.url_for('auth')), data=form_data)

        if token_response.status_code != status.HTTP_200_OK:
            Flash.flash_message(request,
                                f"Failed to login user: {token_response.json().get('detail', 'Unknown error')}")
            return RedirectResponse(str(request.url_for("login")), status_code=status.HTTP_302_FOUND)
        else:
            # request.session["access_token"] = token_response.json()["access_token"]
            # response.set_cookie(key="access_token",
            #                     value=f"Bearer {token_response.json()['access_token']}",
            #                     httponly=True,
            #                     samesite="none")
            Flash.flash_message(request, f"Successful user login for {form.username.data}!")
            return RedirectResponse(str(request.url_for("home")), status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("login.html", {"request": request, "title": "Sign in", "form": form})


@router.post("/register")
async def register(request: Request,
                   user: UserInSchema,
                   db: Session = Depends(get_db)):
    new_user = User(username=user.username,
                    email=user.email)
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    return status.HTTP_200_OK


@router.get("/profile")
async def profile(request: Request,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return status.HTTP_200_OK


@router.get("/read_users")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
