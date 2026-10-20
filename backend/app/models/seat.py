from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MONEY_PRECISION, MONEY_SCALE
from app.models import Event
from app.models.base import Base, UuidPk

if TYPE_CHECKING:
    from app.models.reservation import Reservation


class Seat(Base):
    __tablename__ = "seats"

    seat_id: Mapped[UuidPk]
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Event.event_id, ondelete="CASCADE")
    )
    seat_number: Mapped[str] = mapped_column(String(10))
    price: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE))

    event: Mapped[Event] = relationship(back_populates="seats")
    reservation: Mapped[Reservation | None] = relationship(back_populates="seats")

    __table_args__: tuple[UniqueConstraint, CheckConstraint] = (
        UniqueConstraint(event_id, seat_number),
        CheckConstraint(price >= 0, name="price_non_negative"),
    )
