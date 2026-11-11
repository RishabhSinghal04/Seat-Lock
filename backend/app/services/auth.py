import logging

from sqlalchemy.ext.asyncio import AsyncSession

import app.models.user
import app.repositories.user
import app.schemas.base
from app.core.exceptions.auth import UserAlreadyExistsError
from app.core.exceptions.user import InvalidCredentialsError
from app.core.security import DUMMY_HASH, hash_password, verify_password
from app.models import User
from app.repositories import UserRepository
from app.schemas import MessageResponse, UserLogin, UserSignup
from app.services.verification import VerificationService

logger: logging.Logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        verification: VerificationService,
        session: AsyncSession,
    ) -> None:
        self._users: UserRepository = users
        self._verification: VerificationService = verification
        self._session: AsyncSession = session

    async def signup(
        self, credentials: UserSignup, session: AsyncSession
    ) -> MessageResponse:
        existing: User | None = await self._users.get_by_email(credentials.email)

        if existing:
            logger.info("signup rejected: user_id=%s already registered", existing.uid)
            if not existing.is_verified:
                await self._verification.issue(existing)
            raise UserAlreadyExistsError()

        user = User(
            email=credentials.email,
            password_hash=await hash_password(credentials.password),
        )
        await self._users.add(user)
        await self._session.commit()
        logger.info("user created: %s", user.uid)
        await self._verification.issue(user)
        return MessageResponse(message="Verification code sent to your email.")

    async def login(self, credentials: UserLogin) -> MessageResponse:
        user: app.models.user.User | None = await self._users.get_by_email(
            credentials.email
        )
        is_password_valid: bool = await verify_password(
            user.password_hash if user else DUMMY_HASH, credentials.password
        )
        if not user or not is_password_valid or not user.is_active:
            logger.info("login failed: user_id=%s", user.uid if user else None)
            raise InvalidCredentialsError()

        logger.info("login password accepted: user_id=%s", user.uid)
        await self._verification.issue(user)
        return MessageResponse(
            message="Your sign-in code has been sent to your registered email address."
        )
