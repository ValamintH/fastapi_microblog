import uvicorn
from config import SECRET_KEY
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.auth import router as auth_router
from routers.front import router as front_router
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

middleware = [Middleware(SessionMiddleware, secret_key=SECRET_KEY)]

app = FastAPI(middleware=middleware)
app.mount(
    "/static/",
    StaticFiles(directory="static", html=True),
    name="static",
)
app.include_router(auth_router)
app.include_router(front_router)

if __name__ == "__main__":
    uvicorn.run(app, port=8080)
