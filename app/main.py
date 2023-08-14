from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.forms import LoginForm


middleware = [Middleware(SessionMiddleware, secret_key='super-secret')]
app = FastAPI(middleware=middleware)
app.mount("/static/", StaticFiles(directory='static', html=True), name="static")
templates = Jinja2Templates(directory="templates")


def flash(request: Request, message: str) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
        request.session["_messages"].append(message)


def get_flashed_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []


templates.env.globals['get_flashed_messages'] = get_flashed_messages


@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
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


@app.route("/login", methods=["GET", "POST"])
async def login(request: Request):
    form = await LoginForm.from_formdata(request)

    if await form.validate_on_submit():
        flash(request, f"Login requested for user {form['username'].data}, remember_me={form['remember_me'].data}")
        return RedirectResponse(request.url_for("home"), status_code=302)

    return templates.TemplateResponse("login.html", {"request": request, "form": form})
