from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import router
from app.config import SECRET_KEY


middleware = [Middleware(SessionMiddleware, secret_key=SECRET_KEY)]
app = FastAPI(middleware=middleware)
app.mount("/static/", StaticFiles(directory='static', html=True), name="static")
app.include_router(router)
