from fastapi import Request
from config import templates


class Flash:
    def flash_message(self, request: Request, message: str) -> None:
        """Add message in session's list of messages"""

        if "_messages" not in request.session:
            request.session["_messages"] = []
            request.session["_messages"].append(message)

    def get_flashed_messages(self, request: Request):
        """Return list with all messages and delete them from session"""

        return request.session.pop("_messages") if "_messages" in request.session else []


templates.env.globals['Flash'] = Flash
