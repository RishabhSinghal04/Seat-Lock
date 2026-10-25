from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    MAX_CURRENCY_LENGTH,
    MAX_EVENT_NAME_LENGTH,
    MAX_ONLINE_URL_LENGTH,
    MAX_TIMEZONE_LENGTH,
)
from app.core.enums import EventFormat, EventStatus
from app.models.base import Base, CreatedAt, UuidPk
from app.models.venue import Venue

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.reservation import Reservation
    from app.models.seat import Seat
    from app.models.user import User


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[UuidPk]
    event_name: Mapped[str] = mapped_column(String(MAX_EVENT_NAME_LENGTH))
    venue_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(Venue.venue_id, ondelete="RESTRICT"), index=True
    )
    event_format: Mapped[EventFormat] = mapped_column(
        Enum(EventFormat, native_enum=False),
        default=EventFormat.IN_PERSON,
        server_default=EventFormat.IN_PERSON.name,
        index=True,
    )
    starts_at: Mapped[datetime] = mapped_column(index=True)
    ends_at: Mapped[datetime] = mapped_column()
    # Service rule: create exactly "capacity" seat rows (named ONLINE-n if virtual)
    capacity: Mapped[int] = mapped_column()
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, native_enum=False),
        default=EventStatus.SCHEDULED,
        server_default=EventStatus.SCHEDULED.name,
        index=True,
    )
    currency: Mapped[str] = mapped_column(String(MAX_CURRENCY_LENGTH))
    # Never return this in public responses, only users with a CONFIRMED reservation
    online_url: Mapped[str | None] = mapped_column(String(MAX_ONLINE_URL_LENGTH))
    timezone: Mapped[str] = mapped_column(String(MAX_TIMEZONE_LENGTH))
    created_at: Mapped[CreatedAt]

    venue: Mapped[Venue | None] = relationship(back_populates="events")
    organizers: Mapped[list[User]] = relationship(
        secondary="event_organizers",
        back_populates="organized_events",
        passive_deletes=True,
    )
    categories: Mapped[list[Category]] = relationship(
        secondary="event_categories", passive_deletes=True
    )
    reservations: Mapped[list[Reservation]] = relationship(
        back_populates="event", passive_deletes="all"
    )
    seats: Mapped[list[Seat]] = relationship(
        back_populates="event", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__: tuple[CheckConstraint, ...] = (
        CheckConstraint(capacity > 0, name="capacity_positive"),
        CheckConstraint(ends_at > starts_at, name="ends_after_start"),
        CheckConstraint(
            ((event_format == EventFormat.VIRTUAL) & (venue_id.is_(None)))
            | ((event_format != EventFormat.VIRTUAL) & venue_id.is_not(None)),
            name="venue_matches_event_format",
        ),
        CheckConstraint(
            (event_format == EventFormat.IN_PERSON) | (online_url.is_not(None)),
            name="online_has_url",
        ),
        CheckConstraint(func.length(currency) == 3, name="currency_iso_length"),
    )
