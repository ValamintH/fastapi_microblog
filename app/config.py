from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = 'secret-key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")
