from typing import Callable

import httpx
from db import get_db
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRoute
from flash import Flash, templates
from forms import LoginForm, RegistrationForm
from models import User
from security import get_current_user
from sqlalchemy.orm import Session


class ContextIncludedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            new_headers = request.headers.mutablecopy()
            new_headers.append(
                "authorization", f"Bearer {request.session['access_token']}"
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
    user = {"username": "Miguel"}
    posts = [
        {
            "author": {"username": "John"},
            "body": "Beautiful day in Portland!",
        },
        {
            "author": {"username": "Susan"},
            "body": "The Avengers movie was so cool!",
        },
    ]
    return templates.TemplateResponse(
        "home.html", {"request": request, "user": user, "posts": posts}
    )


@router.get("/login", response_class=HTMLResponse)
@router.post("/login", response_class=RedirectResponse)
async def login(request: Request):
    form = await LoginForm.from_formdata(request)
    if await form.validate_on_submit():
        form_data = {
            "username": form.username.data,
            "password": form.password.data,
        }
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                str(request.url_for("auth")), data=form_data
            )

        if token_response.status_code != status.HTTP_200_OK:
            error = token_response.json().get("detail", "Unknown error")
            Flash.flash_message(
                request,
                f"Failed to login user: {error}",
            )
            return RedirectResponse(
                str(request.url_for("login")),
                status_code=status.HTTP_302_FOUND,
            )
        else:
            token = token_response.json()["access_token"]
            request.session["access_token"] = token
            Flash.flash_message(
                request, f"Successful user login for {form.username.data}!"
            )
            return RedirectResponse(
                str(request.url_for("home")), status_code=status.HTTP_302_FOUND
            )

    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "Sign in", "form": form}
    )


@router.get("/register", response_class=HTMLResponse)
@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    form = await RegistrationForm.from_formdata(request)

    if await form.validate_on_submit():

        # this could be a request to backend
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.add(new_user)
        db.commit()

        Flash.flash_message(
            request, f"Successfully registered user {form.username.data}!"
        )
        return RedirectResponse(
            str(request.url_for("login")),
            status_code=status.HTTP_302_FOUND,
        )

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": "Registration",
            "form": form,
        },
    )


@router.get("/profile")
async def profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = [
        {"author": current_user.username, "body": "Test post #1"},
        {"author": current_user.username, "body": "Test post #2"},
    ]
    return templates.TemplateResponse(
        "user.html", {"request": request, "user": current_user, "posts": posts}
    )


@router.get("/read_users")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
