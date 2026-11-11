import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import UserRepository
from app.schemas import ProfileUpdate, UserResponse

logger: logging.Logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession, users: UserRepository) -> None:
        self._session: AsyncSession = session
        self._users: UserRepository = users

    async def update_profile(self, info: ProfileUpdate, user: User) -> UserResponse:
        logger.debug("update information: user_id=%s", user.uid)
        changes = info.model_dump(exclude_unset=True)
        if changes:
            for field, value in changes.items():
                setattr(user, field, value)
            await self._session.commit()
            logger.info("profile updated: user_id=%s", user.uid)
        return UserResponse.model_validate(user)

    async def delete(self, user: User) -> None:
        logger.debug("delete user: user_id=%s", user.uid)
        user_id: uuid.UUID = user.uid
        await self._users.delete(user)
        await self._session.commit()
        logger.info("user deleted: user_id=%s", user_id)
