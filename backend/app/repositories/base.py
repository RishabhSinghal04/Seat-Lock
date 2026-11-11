from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRespository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def flush_or_raise(self, error: type[Exception]) -> None:
        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise error() from exc
