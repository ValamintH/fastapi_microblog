import email.utils
import logging
import smtplib
from email.message import EmailMessage
from logging.handlers import SMTPHandler

from celery import Celery

celery_app = Celery("celery_app", broker="pyamqp://")


@celery_app.task
def send_email(port, mailhost, timeout, fromaddr, toaddrs, subject, content, username, password):
    if not port:
        port = smtplib.SMTP_PORT
    with smtplib.SMTP_SSL(mailhost, port, timeout=timeout) as smtp:
        msg = EmailMessage()
        msg["From"] = fromaddr
        msg["To"] = ",".join(toaddrs)
        msg["Subject"] = subject
        msg["Date"] = email.utils.localtime()
        msg.set_content(content)
        if username:
            smtp.login(username, password)
        smtp.send_message(msg)


class MailHandler(SMTPHandler):
    def __init__(
        self, mailhost, fromaddr, toaddrs, subject, credentials=None, secure=None, timeout=5.0
    ):
        self.password = None
        super().__init__(mailhost, fromaddr, toaddrs, subject, credentials, secure, timeout)

    def emit(self, record):
        try:
            send_email.delay(
                self.mailport,
                self.mailhost,
                self.timeout,
                self.fromaddr,
                self.toaddrs,
                self.getSubject(record),
                self.format(record),
                self.username,
                self.password,
            )
        except Exception:
            self.handleError(record)


def set_mail_handler(mail_config):
    if mail_config.MAIL_SERVER:
        auth = None
        if mail_config.MAIL_USERNAME or mail_config.MAIL_PASSWORD:
            auth = (mail_config.MAIL_USERNAME, mail_config.MAIL_PASSWORD)
        secure = None
        if mail_config.MAIL_USE_TLS:
            secure = ()
        mail_handler = MailHandler(
            mailhost=(mail_config.MAIL_SERVER, mail_config.MAIL_PORT),
            fromaddr=mail_config.MAIL_USERNAME,
            toaddrs=mail_config.ADMINS,
            subject="Microblog Failure",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        logging.getLogger("uvicorn.error").addHandler(mail_handler)
