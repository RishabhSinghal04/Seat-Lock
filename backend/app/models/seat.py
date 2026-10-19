from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.constants import DECIMAL_PLACES, MAX_INTEGER_DIGITS, SeatStatus
from app.models.event import Event

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.hold import Hold


class Seat(Base):
    __tablename__ = "seats"

    seat_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid7, primary_key=True)
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Event.event_id, ondelete="CASCADE")
    )
    seat_number: Mapped[str] = mapped_column(String(10))
    price: Mapped[Decimal] = mapped_column(Numeric(MAX_INTEGER_DIGITS, DECIMAL_PLACES))
    seat_status: Mapped[SeatStatus] = mapped_column(
        Enum(SeatStatus, native_enum=False),
        default=SeatStatus.AVAILABLE,
        server_default=SeatStatus.AVAILABLE.name,
        index=True,
    )

    event: Mapped[Event] = relationship(back_populates="seats")
    hold: Mapped[Hold | None] = relationship(
        back_populates="seat", cascade="all, delete-orphan", passive_deletes=True
    )
    booking: Mapped[Booking | None] = relationship(
        back_populates="seat", passive_deletes=True
    )

    __table_args__: tuple[UniqueConstraint, CheckConstraint] = (
        UniqueConstraint(event_id, seat_number),
        CheckConstraint(price >= 0, name="price_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<Seat(seat_id={self.seat_id}, seat_number={self.seat_number})>"
