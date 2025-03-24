import smtplib
import random
import os
from email.mime.text import MIMEText
import traceback

from dotenv import load_dotenv
from jinja2 import Template, Environment
from jinja2.loaders import FileSystemLoader


from server.app.utils.logger import logger


load_dotenv()


SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


env = Environment(loader=FileSystemLoader("server/app/templates"))

template = env.get_template("reset_password.html")

def generate_code():
    return str(random.randint(100000, 999999))


def send_reset_code(email: str, code: str):
    subject = "Password reset code"

    html = template.render(code=code)

    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.sendmail(SMTP_USER, email, msg.as_string())

        return True
    except Exception as e:
        traceback.print_exc()
        logger.critical(
            "Email sending failed:\n%s%s",
            " "*10,
            repr(e)
        )

        return False
