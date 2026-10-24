from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Constraint,
    Enum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    MAX_PAYMENT_REFERENCE_LENGTH,
    MONEY_PRECISION,
    MONEY_SCALE,
)
from app.core.enums import ReservationStatus
from app.models.base import Base, CreatedAt, UuidPk
from app.models.event import Event
from app.models.user import User

if TYPE_CHECKING:
    from app.models.refund import Refund
    from app.models.reservation_seat import ReservationSeat


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id: Mapped[UuidPk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.user_id, ondelete="RESTRICT"), index=True
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Event.event_id, ondelete="RESTRICT"), index=True
    )
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, native_enum=False),
        default=ReservationStatus.HELD,
        server_default=ReservationStatus.HELD.name,
    )
    expires_at: Mapped[datetime | None] = mapped_column(index=True)
    payment_reference: Mapped[str | None] = mapped_column(
        String(MAX_PAYMENT_REFERENCE_LENGTH), unique=True
    )
    amount_paid: Mapped[Decimal | None] = mapped_column(
        Numeric(MONEY_PRECISION, MONEY_SCALE)
    )
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[CreatedAt]

    user: Mapped[User] = relationship(back_populates="reservations")
    event: Mapped[Event] = relationship(back_populates="reservations")
    reservation_seats: Mapped[list[ReservationSeat]] = relationship(
        back_populates="reservation", passive_deletes="all"
    )
    refunds: Mapped[list[Refund]] = relationship(
        back_populates="reservation", passive_deletes="all"
    )

    __table_args__: tuple[Constraint, ...] = (
        CheckConstraint(
            (status != ReservationStatus.CONFIRMED)
            | (payment_reference.is_not(None) & amount_paid.is_not(None)),
            name="confirmed_has_payment",
        ),
        CheckConstraint(
            (status != ReservationStatus.HELD) | (expires_at.is_not(None)),
            name="held_has_expiry",
        ),
        CheckConstraint(amount_paid >= 0, name="amount_non_negative"),
    )
