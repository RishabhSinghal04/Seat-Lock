from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, func, true
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.elements import BinaryExpression

from app.core.constants import MAX_EMAIL_LENGTH, MAX_NAME_LENGTH
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.reservation import Reservation


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(MAX_EMAIL_LENGTH), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(MAX_NAME_LENGTH))
    dob: Mapped[date | None]
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    email_verified_at: Mapped[datetime | None]
    password_changed_at: Mapped[datetime | None]
    pending_email: Mapped[str | None] = mapped_column(
        String(MAX_EMAIL_LENGTH), unique=True
    )

    organized_events: Mapped[list[Event]] = relationship(
        secondary="event_organizers", back_populates="organizers", passive_deletes=True
    )
    reservations: Mapped[list[Reservation]] = relationship(
        back_populates="user", passive_deletes="all"
    )

    @hybrid_property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None

    @is_verified.inplace.expression
    @classmethod
    def _is_verified_expression(cls) -> BinaryExpression[bool]:
        return cls.email_verified_at.is_not(None)

    __table_args__: tuple[CheckConstraint] = (
        CheckConstraint(email == func.lower(email), name="email_lowercase"),
    )
