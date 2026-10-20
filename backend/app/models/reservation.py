import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    MAX_PAYMENT_REFERENCE_LENGTH,
    MONEY_PRECISION,
    MONEY_SCALE,
)
from app.core.enums import ReservationStatus
from app.models.base import Base, CreatedAt, UuidPk
from app.models.seat import Seat
from app.models.user import User


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id: Mapped[UuidPk]
    seat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Seat.seat_id, ondelete="RESTRICT"), unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.user_id, ondelete="RESTRICT"), index=True
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
    created_at: Mapped[CreatedAt]

    seat: Mapped[Seat] = relationship(back_populates="reservation")
    user: Mapped[User] = relationship(back_populates="reservation")

    __table_args__: tuple[CheckConstraint, CheckConstraint] = (
        CheckConstraint(
            (status == ReservationStatus.CONFIRMED) | (payment_reference.is_not(None)),
            # "status <> 'CONFIRMED' OR payment_reference IS NOT NULL",
            name="confirmed_has_payment",
        ),
        CheckConstraint(amount_paid >= 0, name="amount_non_negative"),
    )
