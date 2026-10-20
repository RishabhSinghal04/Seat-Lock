from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MAX_EMAIL_LENGTH
from app.models.base import Base, CreatedAt, UuidPk

if TYPE_CHECKING:
    from app.models.reservation import Reservation


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[UuidPk]
    email: Mapped[str] = mapped_column(String(MAX_EMAIL_LENGTH), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    is_verified: Mapped[bool] = mapped_column(default=False, server_default=false())
    pending_email: Mapped[str | None] = mapped_column(
        String(MAX_EMAIL_LENGTH), unique=True
    )
    created_at: Mapped[CreatedAt]

    reservations: Mapped[list[Reservation]] = relationship(back_populates="user")
# if user can organize an event or events then why not create a relationship with event?
