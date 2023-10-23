import uvicorn
from config import SECRET_KEY, MailConfig, templates
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.auth import router as auth_router
from routers.front import router as front_router
from set_uvicorn_handlers import set_file_handler, set_mail_handler
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


@app.on_event("startup")
async def startup_event():
    set_mail_handler(MailConfig())
    set_file_handler()


@app.exception_handler(404)
@app.exception_handler(403)
async def http_exc_handler(request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "detail": exc.detail, "status": exc.status_code},
        exc.status_code,
    )


@app.exception_handler(500)
async def any_exc_handler(request, _):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "detail": "Unknown error", "status": 500},
        500,
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
