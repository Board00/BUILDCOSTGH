import logging
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
DEFAULT_SENDER = "konradkakraba1234@gmail.com"


def _send_email(recipient: str, subject: str, body: str) -> None:
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_password:
        logger.warning("SMTP_PASSWORD is not configured; email was not sent to %s", recipient)
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = os.getenv("SMTP_FROM", os.getenv("SMTP_USERNAME", DEFAULT_SENDER))
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP(
        os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "587"))
    ) as smtp:
        smtp.starttls()
        smtp.login(os.getenv("SMTP_USERNAME", DEFAULT_SENDER), smtp_password)
        smtp.send_message(message)


def send_welcome_email(recipient: str, username: str) -> None:
    try:
        _send_email(
            recipient,
            "Welcome to BuildCost",
            f"Hello {username},\n\nYour BuildCost account has been created successfully.\n\nYou can now log in and start planning your project.\n\nThe BuildCost team",
        )
    except Exception:
        logger.exception("Unable to send welcome email to %s", recipient)


def send_password_reset_email(recipient: str, username: str, reset_url: str) -> None:
    try:
        _send_email(
            recipient,
            "Reset your BuildCost password",
            f"Hello {username},\n\nWe received a request to reset your BuildCost password. Use the link below within 30 minutes:\n\n{reset_url}\n\nIf you did not request this, you can ignore this email.\n\nThe BuildCost team",
        )
    except Exception:
        logger.exception("Unable to send password reset email to %s", recipient)