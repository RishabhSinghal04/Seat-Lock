import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MONEY_PRECISION, MONEY_SCALE
from app.models.base import Base
from app.models.reservation import Reservation
from app.models.seat import Seat


class ReservationSeat(Base):
    __tablename__ = "reservation_seats"

    reservation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Reservation.reservation_id, ondelete="RESTRICT"), primary_key=True
    )
    seat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Seat.seat_id, ondelete="RESTRICT"), primary_key=True
    )
    price: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())

    reservation: Mapped[Reservation] = relationship(back_populates="reservation_seats")
    seat: Mapped[Seat] = relationship(back_populates="reservation_seats")

    __table_args__: tuple[CheckConstraint, Index] = (
        CheckConstraint(price >= 0, name="price_non_negative"),
        Index(
            "uq_reservation_seats_one_active_owner",
            seat_id,
            unique=True,
            postgresql_where=is_active.is_(True),
        ),
    )
