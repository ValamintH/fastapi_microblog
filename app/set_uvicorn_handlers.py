import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler


def set_mail_handler(mail_config):
    if mail_config.MAIL_SERVER:
        auth = None
        if mail_config.MAIL_USERNAME or mail_config.MAIL_PASSWORD:
            auth = (mail_config.MAIL_USERNAME, mail_config.MAIL_PASSWORD)
        secure = None
        if mail_config.MAIL_USE_TLS:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(mail_config.MAIL_SERVER, mail_config.MAIL_PORT),
            fromaddr="no-reply@" + mail_config.MAIL_SERVER,
            toaddrs=mail_config.ADMINS,
            subject="Microblog Failure",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        logging.getLogger("uvicorn.error").addHandler(mail_handler)


def set_file_handler():
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/microblog.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    file_handler.setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").addHandler(file_handler)
