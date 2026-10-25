import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    MAX_PAYMENT_REFERENCE_LENGTH,
    MONEY_PRECISION,
    MONEY_SCALE,
)
from app.core.enums import RefundStatus
from app.models.base import Base, CreatedAt, UuidPk
from app.models.reservation import Reservation
from app.models.seat import Seat


class Refund(Base):
    __tablename__ = "refunds"

    refund_id: Mapped[UuidPk]
    reservation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Reservation.reservation_id, ondelete="RESTRICT"), index=True
    )
    seat_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(Seat.seat_id, ondelete="RESTRICT")
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE))
    status: Mapped[RefundStatus] = mapped_column(
        Enum(RefundStatus, native_enum=False),
        default=RefundStatus.PENDING,
        server_default=RefundStatus.PENDING.name,
    )
    refund_reference: Mapped[str | None] = mapped_column(
        String(MAX_PAYMENT_REFERENCE_LENGTH), unique=True
    )
    reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[CreatedAt]

    reservation: Mapped[Reservation] = relationship(back_populates="refunds")

    __table_args__: tuple[CheckConstraint] = (
        CheckConstraint(amount > 0, name="amount_positive"),
    )
