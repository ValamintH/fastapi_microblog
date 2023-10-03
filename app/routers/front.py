import httpx
from config import templates
from dependencies.db import get_db
from dependencies.security import get_current_user
from dependencies.set_last_seen import set_last_seen
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from flash import Flash
from forms import EditProfileForm, LoginForm, RegistrationForm
from models.users import User
from queries import get_user_by_name
from sqlalchemy.orm import Session

router = APIRouter(dependencies=[Depends(set_last_seen)])


@router.get("/", response_class=HTMLResponse)
@router.get("/home", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: User = Depends(get_current_user),
):
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
        "home.html", {"request": request, "user": current_user, "posts": posts}
    )


@router.get("/login", response_class=HTMLResponse)
@router.post("/login", response_class=RedirectResponse)
async def login(request: Request, response: Response):
    form = await LoginForm.from_formdata(request)
    if await form.validate_on_submit():
        form_data = {
            "username": form.username.data,
            "password": form.password.data,
        }
        async with httpx.AsyncClient() as client:
            token_response = await client.post(str(request.url_for("auth")), data=form_data)

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
            response.set_cookie(
                key="access_token",
                value=f"Bearer {token_response.json()['access_token']}",
                httponly=True,
                samesite="strict",
            )
            Flash.flash_message(request, f"Successful user login for {form.username.data}!")
            return RedirectResponse(
                str(request.url_for("home")),
                status_code=status.HTTP_302_FOUND,
                headers=response.headers,
            )

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": "Login",
            "form": form,
        },
    )


@router.post("/logout")
def logout(request: Request, response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="strict",
    )
    return RedirectResponse(
        str(request.url_for("home")),
        status_code=status.HTTP_302_FOUND,
        headers=response.headers,
    )


@router.get("/register", response_class=HTMLResponse)
@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    form = await RegistrationForm.from_formdata(request)

    if await form.validate_on_submit():
        # this could be a query
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.add(new_user)
        db.commit()

        Flash.flash_message(request, f"Successfully registered user {form.username.data}!")
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


@router.get("/profile/{username}")
async def profile(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page_user = await get_user_by_name(username=username, db=db)
    if not page_user:
        raise HTTPException(status_code=404, detail="User not found")

    posts = [
        {"author": page_user, "body": "Test post #1"},
        {"author": page_user, "body": "Test post #2"},
    ]
    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user": current_user,
            "page_user": page_user,
            "posts": posts,
        },
    )


@router.get("/edit_profile")
@router.post("/edit_profile")
async def edit_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not logged in")

    form = await EditProfileForm.from_formdata(request)
    if await form.validate_on_submit():
        # this could be a query
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.commit()
        Flash.flash_message(request, "Your changes have been saved")
        return RedirectResponse(
            str(request.url_for("edit_profile")),
            status_code=status.HTTP_302_FOUND,
        )
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return templates.TemplateResponse(
        "edit_profile.html",
        {"request": request, "title": "Edit Profile", "form": form},
    )


@router.get("/read_users")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
