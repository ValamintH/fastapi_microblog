from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict

SQLALCHEMY_DATABASE_URI = "sqlite:///example.db"
SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
templates = Jinja2Templates(directory="templates")


class MailConfig(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)

    MAIL_SERVER: str = None
    MAIL_PORT: int = 25
    MAIL_USE_TLS: str = None
    MAIL_USERNAME: str = None
    MAIL_PASSWORD: str = None
    ADMINS: list[str] = ["your-email@example.com"]
