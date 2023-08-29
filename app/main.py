from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from routers import auth_router, front_router
from config import SECRET_KEY


middleware = [Middleware(SessionMiddleware, secret_key=SECRET_KEY)]

app = FastAPI(middleware=middleware)
app.mount("/static/", StaticFiles(directory='static', html=True), name="static")
app.include_router(auth_router)
app.include_router(front_router)
