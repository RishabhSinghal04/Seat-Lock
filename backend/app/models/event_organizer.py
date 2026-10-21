import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.event import Event
from app.models.user import User


class EventOrganizer(Base):
    __tablename__ = "event_organizer"

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Event.event_id, ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.user_id, ondelete="RESTRICT"), primary_key=True
    )
