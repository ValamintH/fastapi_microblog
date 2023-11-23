import logging
import os
from logging.handlers import RotatingFileHandler


def set_file_handler():
    if not os.path.exists("../logs"):
        os.mkdir("../logs")
    file_handler = RotatingFileHandler("../logs/microblog.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    file_handler.setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").addHandler(file_handler)
