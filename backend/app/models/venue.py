from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    MAX_CITY_LENGTH,
    MAX_COUNTRY_CODE_LENGTH,
    MAX_LOCALITY_LENGTH,
    MAX_POSTAL_CODE_LENGTH,
    MAX_STATE_LENGTH,
    MAX_STREET_LENGTH,
    MAX_TIMEZONE_LENGTH,
    MAX_VENUE_LENGTH,
)
from app.models.base import Base, UuidPk

if TYPE_CHECKING:
    from app.models.event import Event


class Venue(Base):
    __tablename__ = "venues"

    venue_id: Mapped[UuidPk]
    name: Mapped[str] = mapped_column(String(MAX_VENUE_LENGTH))
    street: Mapped[str] = mapped_column(String(MAX_STREET_LENGTH))
    locality: Mapped[str | None] = mapped_column(String(MAX_LOCALITY_LENGTH))
    city: Mapped[str] = mapped_column(String(MAX_CITY_LENGTH), index=True)
    state: Mapped[str | None] = mapped_column(String(MAX_STATE_LENGTH))
    postal_code: Mapped[str | None] = mapped_column(String(MAX_POSTAL_CODE_LENGTH))
    country_code: Mapped[str] = mapped_column(String(MAX_COUNTRY_CODE_LENGTH))
    timezone: Mapped[str] = mapped_column(String(MAX_TIMEZONE_LENGTH))

    events: Mapped[list[Event]] = relationship(
        back_populates="venue", passive_deletes="all"
    )
