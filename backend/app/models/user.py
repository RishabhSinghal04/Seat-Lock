from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.constants import MAX_EMAIL_LENGTH

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.hold import Hold


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid7, primary_key=True)
    email: Mapped[str] = mapped_column(String(MAX_EMAIL_LENGTH), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    is_verified: Mapped[bool] = mapped_column(default=False, server_default=false())
    pending_email: Mapped[str | None] = mapped_column(String(MAX_EMAIL_LENGTH))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    holds: Mapped[list[Hold]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    bookings: Mapped[list[Booking]] = relationship(
        back_populates="user", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id})>"
