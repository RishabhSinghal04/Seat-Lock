from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MAX_EVENT_NAME_LENGTH
from app.core.enums import EventStatus
from app.models.base import Base, CreatedAt, UuidPk
from app.models.venue import Venue

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.seat import Seat
    from app.models.user import User


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[UuidPk]
    event_name: Mapped[str] = mapped_column(String(MAX_EVENT_NAME_LENGTH))
    venue_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Venue.venue_id, ondelete="RESTRICT"), index=True
    )
    starts_at: Mapped[datetime] = mapped_column(index=True)
    ends_at: Mapped[datetime] = mapped_column()
    capacity: Mapped[int] = mapped_column()
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, native_enum=False),
        default=EventStatus.SCHEDULED,
        server_default=EventStatus.SCHEDULED.name,
        index=True,
    )
    created_at: Mapped[CreatedAt]

    venue: Mapped[Venue] = relationship(back_populates="events")
    organizers: Mapped[list[User]] = relationship(
        secondary="event_organizer",
        back_populates="organized_events",
        passive_deletes=True,
    )
    reservations: Mapped[list[Reservation]] = relationship(
        back_populates="event", passive_deletes="all"
    )
    seats: Mapped[list[Seat]] = relationship(
        back_populates="event", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__: tuple[CheckConstraint, ...] = (
        CheckConstraint(capacity > 0, name="seats_positive"),
        CheckConstraint(ends_at > starts_at, name="ends_after_start"),
    )
