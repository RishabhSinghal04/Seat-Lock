from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.constants import (
    DECIMAL_PLACES,
    MAX_INTEGER_DIGITS,
    MAX_PAYMENT_REFERENCE_LENGTH,
)
from app.models.seat import Seat
from app.models.user import User


class Booking(Base):
    __tablename__ = "bookings"

    booking_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid7, primary_key=True)
    seat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Seat.seat_id, ondelete="CASCADE"), unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.user_id, ondelete="CASCADE"), index=True
    )
    payment_reference: Mapped[str] = mapped_column(
        String(MAX_PAYMENT_REFERENCE_LENGTH), unique=True
    )
    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(MAX_INTEGER_DIGITS, DECIMAL_PLACES)
    )
    confirmed_at: Mapped[datetime] = mapped_column(server_default=func.now())

    seat: Mapped[Seat] = relationship(back_populates="booking")
    user: Mapped[User] = relationship(back_populates="bookings")

    def __repr__(self) -> str:
        return f"<Booking(booking_id={self.booking_id})>"
