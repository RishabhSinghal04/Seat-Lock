from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Constraint,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MAX_SEAT_NUMBER_LENGTH, MONEY_PRECISION, MONEY_SCALE
from app.models.base import Base, UuidPk
from app.models.event import Event

if TYPE_CHECKING:
    from app.models.reservation_seat import ReservationSeat


class Seat(Base):
    __tablename__ = "seats"

    seat_id: Mapped[UuidPk]
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Event.event_id, ondelete="CASCADE")
    )
    seat_number: Mapped[str] = mapped_column(String(MAX_SEAT_NUMBER_LENGTH))
    price: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE))

    event: Mapped[Event] = relationship(back_populates="seats")
    reservation_seats: Mapped[list[ReservationSeat]] = relationship(
        back_populates="seat", passive_deletes="all"
    )

    __table_args__: tuple[Constraint, ...] = (
        CheckConstraint(price >= 0, name="price_non_negative"),
        UniqueConstraint(event_id, seat_number),
    )
