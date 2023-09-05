from fastapi.templating import Jinja2Templates


SECRET_KEY = 'secret-key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
templates = Jinja2Templates(directory="templates")
