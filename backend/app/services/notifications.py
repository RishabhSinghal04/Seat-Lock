from dataclasses import dataclass
from datetime import timedelta
from typing import Final

from app.core.enums import TokenPurpose
from app.services.mailer import EmailSender


@dataclass(frozen=True, slots=True)
class _Template:
    subject: str
    reason: str


_TEMPLATES: Final[dict[TokenPurpose, _Template]] = {
    TokenPurpose.EMAIL_VERIFICATION: _Template(
        subject="Seat Lock - Verify your email",
        reason="verify your email address",
    ),
}


def _minutes(ttl: timedelta) -> str:
    n: int = max(1, int(ttl.total_seconds() // 60))
    return f"{n} minute{'s' if n != 1 else ''}"


class EmailCodeNotifier:
    def __init__(self, mailer: EmailSender) -> None:
        self._mailer: EmailSender = mailer

    async def send_code(
        self, *, to: str, code: str, purpose: TokenPurpose, ttl: timedelta
    ) -> None:
        try:
            template: _Template = _TEMPLATES[purpose]
        except KeyError:
            raise ValueError(f"no email template for purpose {purpose!r}") from None
        await self._mailer.send(
            to=to,
            subject=template.subject,
            text=(
                f"Use this code to {template.reason}: {code}\n"
                f"It expires in {_minutes(ttl)}.\n"
                "If you did not request this, you can ignore this email."
            ),
        )
