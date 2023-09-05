from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from routers import auth_router, front_router
from config import SECRET_KEY
import uvicorn


middleware = [Middleware(SessionMiddleware, secret_key=SECRET_KEY)]

app = FastAPI(middleware=middleware)
app.mount("/static/", StaticFiles(directory='static', html=True), name="static")
app.include_router(auth_router)
app.include_router(front_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["Access-Control-Allow-Headers", "Content-Type", "Authorization", "Access-Control-Allow-Origin","Set-Cookie"],
)

if __name__ == "__main__":
    uvicorn.run(app, port=8080)
