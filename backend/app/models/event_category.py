from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.category import Category
from app.models.event import Event


class EventCategory(Base):
    __tablename__ = "event_categories"

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Event.event_id, ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Category.category_id, ondelete="RESTRICT"),
        primary_key=True,
        index=True,
    )
