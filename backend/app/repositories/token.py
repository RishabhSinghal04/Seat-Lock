import hmac
import uuid
from datetime import datetime

from sqlalchemy import select, update

from app.core.enums import TokenPurpose
from app.models import OneTimeToken
from app.repositories.base import BaseRespository


class OneTimeTokenRepository(BaseRespository):
    async def add(self, token: OneTimeToken) -> None:
        self.session.add(token)
        await self.session.flush()

    async def get_active(
        self, user_id: uuid.UUID, purpose: TokenPurpose, now: datetime
    ) -> OneTimeToken | None:
        return await self.session.scalar(
            select(OneTimeToken)
            .where(
                OneTimeToken.user_id == user_id,
                OneTimeToken.purpose == purpose,
                OneTimeToken.consumed_at.is_(None),
                OneTimeToken.expires_at > now,
            )
            .order_by(OneTimeToken.created_at)
            .limit(1)
            .with_for_update()
        )

    async def invalidate_active(
        self, user_id: uuid.UUID, purpose: TokenPurpose, now: datetime
    ) -> None:
        await self.session.scalar(
            update(OneTimeToken)
            .where(
                OneTimeToken.user_id == user_id,
                OneTimeToken.purpose == purpose,
                OneTimeToken.consumed_at.is_(None),
            )
            .values(consumed_at=now)
        )

    def matches(self, token: OneTimeToken, candidate_hash: str) -> bool:
        return hmac.compare_digest(token.token_hash, candidate_hash)
