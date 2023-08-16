from fastapi import Request
from app.config import templates


def flash(request: Request, message: str) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
        request.session["_messages"].append(message)


def get_flashed_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []


templates.env.globals['get_flashed_messages'] = get_flashed_messages
