from fastapi.templating import Jinja2Templates


SECRET_KEY = 'secret-key'
templates = Jinja2Templates(directory="templates")
