from __future__ import annotations

from sqlalchemy import String, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MAX_CATEGORY_NAME_LENGTH, MAX_CATEGORY_SLUG_LENGTH
from app.models.base import Base, UuidPk


class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[UuidPk]
    slug: Mapped[str] = mapped_column(String(MAX_CATEGORY_SLUG_LENGTH), unique=True)
    name: Mapped[str] = mapped_column(String(MAX_CATEGORY_NAME_LENGTH))
    # Retire a category with is_active=False. Never delete old events, keep it.
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
