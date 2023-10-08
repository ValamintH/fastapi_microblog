import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

import uvicorn
from config import SECRET_KEY, MailConfig, templates
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


@app.on_event("startup")
async def startup_event():
    if MailConfig.MAIL_SERVER:
        auth = None
        if MailConfig.MAIL_USERNAME or MailConfig.MAIL_PASSWORD:
            auth = (MailConfig.MAIL_USERNAME, MailConfig.MAIL_PASSWORD)
        secure = None
        if MailConfig.MAIL_USE_TLS:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(MailConfig.MAIL_SERVER, MailConfig.MAIL_PORT),
            fromaddr="no-reply@" + MailConfig.MAIL_SERVER,
            toaddrs=MailConfig.ADMINS,
            subject="Microblog Failure",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        logging.getLogger("uvicorn.error").addHandler(mail_handler)

    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/microblog.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    file_handler.setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").addHandler(file_handler)


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
