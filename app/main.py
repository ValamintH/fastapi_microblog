import uvicorn
from config import SECRET_KEY, templates
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


@app.exception_handler(404)
@app.exception_handler(500)
@app.exception_handler(403)
async def not_found_error(request, exc):
    return templates.TemplateResponse(
        "error.html", {"request": request, "detail": exc.detail}, exc.status_code
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
