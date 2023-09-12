from config import templates
from fastapi import Request


class Flash:
    @staticmethod
    def flash_message(request: Request, message: str) -> None:
        """Add message in session's list of messages"""

        if "_messages" not in request.session:
            request.session["_messages"] = []
            request.session["_messages"].append(message)

    @staticmethod
    def get_flashed_messages(request: Request):
        """Return list with all messages and delete them from session"""

        if "_messages" in request.session:
            return request.session.pop("_messages")
        else:
            return []


templates.env.globals["Flash"] = Flash
