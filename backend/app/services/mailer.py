import logging
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from typing import Protocol

import aiosmtplib

from app.core.config import SMTPConfig
from app.core.exceptions.email import EmailDeliveryError

logger: logging.Logger = logging.getLogger(__name__)


class EmailSender(Protocol):
    async def send(
        self, *, to: str, subject: str, text: str, html: str | None = None
    ) -> None: ...


def build_message(
    *,
    sender_name: str,
    sender_address: str,
    to: str,
    subject: str,
    text: str,
    html: str | None = None,
) -> EmailMessage:
    message: EmailMessage = EmailMessage()
    message["From"] = formataddr(pair=(sender_name, sender_address))
    message["To"] = to
    message["Subject"] = subject
    message["Date"] = formatdate(usegmt=True)
    message["Message-ID"] = make_msgid(domain=(sender_address.rpartition("@")[2]))
    message.set_content(text)
    if html is not None:
        message.add_alternative(html, subtype="html")
    return message


class SMTPMailer:
    def __init__(self, config: SMTPConfig) -> None:
        self._config: SMTPConfig = config

    async def send(
        self, *, to: str, subject: str, text: str, html: str | None = None
    ) -> None:
        message: EmailMessage = build_message(
            sender_name=self._config.EMAIL_FROM_NAME,
            sender_address=self._config.EMAIL_FROM_ADDRESS,
            to=to,
            subject=subject,
            text=text,
            html=html,
        )
        try:
            await aiosmtplib.send(
                message,
                hostname=self._config.SMTP_HOST,
                port=self._config.SMTP_PORT,
                username=self._config.SMTP_USER,
                password=self._config.SMTP_PASSWORD.get_secret_value(),
                use_tls=self._config.SMTP_SECURITY == "tls",
                start_tls=self._config.SMTP_SECURITY == "starttls",
                timeout=self._config.SMTP_TIMEOUT_SECONDS,
            )
        except (aiosmtplib.SMTPException, OSError) as exc:
            logger.exception("email delivery failed")
            raise EmailDeliveryError() from exc
        logger.info("email sent: subject=%r", subject)
