import logging
from datetime import UTC, datetime, timedelta
from typing import Protocol

from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CODE_TTL, MAX_CODE_ATTEMPTS
from app.core.enums import TokenPurpose
from app.core.exceptions.user import InvalidCodeError
from app.core.security import generate_numeric_code, hash_token
from app.models import OneTimeToken, User
from app.repositories import OneTimeTokenRepository

logger: logging.Logger = logging.getLogger(__name__)

_DEFAULT_PURPOSE = TokenPurpose.EMAIL_VERIFICATION


class CodeNotifier(Protocol):  # the only real boundary: external I/O
    async def send_code(
        self, *, to: str, code: str, purpose: TokenPurpose, ttl: timedelta
    ) -> None: ...


def _email_body(code: str) -> str:
    minutes = int(CODE_TTL.total_seconds() // 60)
    unit = "minute" if minutes == 1 else "minutes"
    return (
        f"Your authentication code is {code}.\n"
        f"It expires in {minutes} {unit}.\n"
        "If you did not request this, ignore this email."
    )


class VerificationService:
    def __init__(
        self,
        session: AsyncSession,
        tokens: OneTimeTokenRepository,
        notifier: CodeNotifier,
        secret: SecretStr,
        *,
        ttl: timedelta = CODE_TTL,
        max_attempts: int = MAX_CODE_ATTEMPTS,
    ) -> None:
        self._session: AsyncSession = session
        self._tokens: OneTimeTokenRepository = tokens
        self._notifier: CodeNotifier = notifier
        self._secret: SecretStr = secret
        self._ttl: timedelta = ttl
        self._max_attempts: int = max_attempts

    async def issue(self, user: User, purpose: TokenPurpose = _DEFAULT_PURPOSE) -> None:
        now: datetime = datetime.now(UTC)
        code: str = generate_numeric_code()
        await self._tokens.invalidate_active(user.uid, purpose, now)
        await self._tokens.add(
            OneTimeToken(
                user_id=user.uid,
                purpose=purpose,
                token_hash=hash_token(code, self._secret),
                expires_at=now + self._ttl,
            )
        )
        await self._session.commit()
        await self._notifier.send_code(
            to=user.email, code=code, purpose=purpose, ttl=self._ttl
        )
        logger.info("code issued: user_id=%s purpose=%s", user.uid, purpose)

    async def verify(
        self,
        user: User,
        code: str,
        purpose: TokenPurpose = TokenPurpose.EMAIL_VERIFICATION,
    ) -> None:
        now: datetime = datetime.now(UTC)
        token: OneTimeToken | None = await self._tokens.get_active(
            user.uid, purpose, now
        )
        if token is None or token.attempts >= MAX_CODE_ATTEMPTS:
            logger.info("code rejected: user_id=%s reason=none_or_locked", user.uid)
            raise InvalidCodeError()
        if not self._tokens.matches(token, hash_token(code, self._secret)):
            token.attempts += 1
            await self._session.commit()
            logger.info("code rejected: user_id=%s reason=mismatch", user.uid)
            raise InvalidCodeError()
        token.consumed_at = now
        await self._session.commit()
