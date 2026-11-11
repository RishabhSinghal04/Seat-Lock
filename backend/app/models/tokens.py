import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, String, column, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import TOKEN_HASH_LENGTH
from app.core.enums import TokenPurpose
from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin
from app.models.user import User


class OneTimeToken(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "one_time_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(User.uid, ondelete="CASCADE"))
    purpose: Mapped[TokenPurpose] = mapped_column(Enum(TokenPurpose, native_enum=False))
    token_hash: Mapped[str] = mapped_column(String(TOKEN_HASH_LENGTH))
    attempts: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    expires_at: Mapped[datetime] = mapped_column(index=True)
    consumed_at: Mapped[datetime | None]

    __table_args__: tuple[Index, CheckConstraint] = (
        Index("ix_one_time_tokens_user_purpose", user_id, purpose),
        CheckConstraint(attempts >= 0, "attempts_non_negative"),
    )


class RefreshToken(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.uid, ondelete="CASCADE"), index=True
    )
    family_id: Mapped[uuid.UUID]
    token_hash: Mapped[str] = mapped_column(String(TOKEN_HASH_LENGTH), unique=True)
    expires_at: Mapped[datetime] = mapped_column(index=True)
    revoked_at: Mapped[datetime | None] = mapped_column()
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id", ondelete="SET NULL")
    )

    __table_args__: tuple[CheckConstraint, Index] = (
        CheckConstraint(replaced_by_id != column("id"), name="not_self_replaced"),
        Index(
            "ix_refresh_tokens_family_active",
            "family_id",
            postgresql_where=revoked_at.is_(None),
        ),
    )
