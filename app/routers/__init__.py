from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from app.forms import LoginForm
from app.flash import flash, templates


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.get("/home/", response_class=HTMLResponse)
def home(request: Request):
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


@router.get("/login")
@router.post("/login")
async def login(request: Request):
    form = await LoginForm.from_formdata(request)

    if await form.validate_on_submit():
        flash(request, f"Login requested for user {form['username'].data}, remember_me={form['remember_me'].data}")
        return RedirectResponse(request.url_for("home"), status_code=302)

    return templates.TemplateResponse("login.html", {"request": request, "form": form})



