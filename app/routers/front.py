from fastapi import Request, Depends, APIRouter, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from forms import LoginForm
from flash import templates
from models import User
from db import get_db
from security import get_current_user
from sqlalchemy.orm import Session
from schemas import UserInSchema


router = APIRouter()


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


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request):
    try:
        current_user = await get_current_user()
    except HTTPException:
        return RedirectResponse(request.url_for('home'))

    if current_user:
        return RedirectResponse(request.url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        return status.HTTP_200_OK
    return templates.TemplateResponse("login.html", {"request": request, "title": "Sign in", "form": form})


@router.post("/register")
async def register(user: UserInSchema, db: Session = Depends(get_db)):
    new_user = User(username=user.username,
                    email=user.email)
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    return status.HTTP_200_OK


@router.get("/profile")
async def my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return status.HTTP_200_OK


@router.get("/read_users")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
