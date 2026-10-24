from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MAX_EMAIL_LENGTH
from app.models.base import Base, CreatedAt, UuidPk

if TYPE_CHECKING:
    from app.models.event import Event
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

    organized_events: Mapped[list[Event]] = relationship(
        secondary="event_organizer", back_populates="organizers", passive_deletes=True
    )
    reservations: Mapped[list[Reservation]] = relationship(
        back_populates="user", passive_deletes="all"
    )
