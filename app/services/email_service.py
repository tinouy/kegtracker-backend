import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from app.core.config import get_settings
import os

settings = get_settings()
FROM_ADDRESS = getattr(settings, 'SMTP_FROM', settings.SMTP_USER)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../email/templates')
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)

async def send_email(to: str, subject: str, template_name: str, context: dict):
    content = render_template(template_name, context)
    message = EmailMessage()
    message["From"] = FROM_ADDRESS
    message["To"] = to
    message["Subject"] = subject
    message.set_content(content, subtype="html")
    print('SMTP_HOST:', settings.SMTP_HOST)
    print('SMTP_PORT:', settings.SMTP_PORT)
    print('SMTP_USER:', settings.SMTP_USER)
    print('SMTP_FROM:', settings.SMTP_FROM)
    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
    )

async def send_invite_email(to: str, invite_link: str):
    await send_email(
        to=to,
        subject="KegTracker Registration",
        template_name="register_user.html",
        context={"registration_link": invite_link}
    )
