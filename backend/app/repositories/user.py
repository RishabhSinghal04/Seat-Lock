import uuid

from sqlalchemy import select

from app.core.exceptions.auth import UserAlreadyExistsError
from app.core.exceptions.user import ResourceInUseError
from app.models import User
from app.repositories.base import BaseRespository


class UserRepository(BaseRespository):
    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def add(self, user: User) -> None:
        self.session.add(user)
        await self.flush_or_raise(UserAlreadyExistsError)

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.flush_or_raise(ResourceInUseError)
