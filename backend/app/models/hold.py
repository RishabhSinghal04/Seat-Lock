from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.constants import HOLD_DURATION_INTERVAL
from app.models.seat import Seat
from app.models.user import User


class Hold(Base):
    __tablename__ = "holds"

    hold_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid7, primary_key=True)
    seat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Seat.seat_id, ondelete="CASCADE"), unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.user_id, ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now() + HOLD_DURATION_INTERVAL, index=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    seat: Mapped[Seat] = relationship(back_populates="hold")
    user: Mapped[User] = relationship(back_populates="holds")

    def __repr__(self) -> str:
        return f"<Hold(hold_id={self.hold_id})>"
