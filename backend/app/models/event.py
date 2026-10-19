from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.constants import MAX_EVENT_NAME_LENGTH, MAX_VENUE_LENGTH
from app.models.user import User

if TYPE_CHECKING:
    from app.models.seat import Seat


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid7, primary_key=True)
    event_name: Mapped[str] = mapped_column(String(MAX_EVENT_NAME_LENGTH))
    venue: Mapped[str] = mapped_column(String(MAX_VENUE_LENGTH), index=True)
    starts_at: Mapped[datetime] = mapped_column(index=True)
    organizer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.user_id, ondelete="RESTRICT", index=True)
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    organizer: Mapped[User] = relationship()
    seats: Mapped[list[Seat]] = relationship(
        back_populates="event", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Event(event_id={self.event_id}, event_name={self.event_name})>"
