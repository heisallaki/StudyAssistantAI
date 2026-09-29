import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class EmailSendError(Exception):
    pass


def send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        raise EmailSendError("SMTP is not configured. Set SMTP_USERNAME and SMTP_PASSWORD.")

    message = EmailMessage()
    message["Subject"] = subject
    from_address = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    message["From"] = f"{settings.SMTP_FROM_NAME} <{from_address}>"
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
    except smtplib.SMTPException as error:
        logger.error("Failed to send email to %s: %s", to_email, error)
        raise EmailSendError("Could not send email.") from error
    except OSError as error:
        logger.error("Could not connect to SMTP server %s:%s: %s", settings.SMTP_HOST, settings.SMTP_PORT, error)
        raise EmailSendError("Could not connect to the email server.") from error