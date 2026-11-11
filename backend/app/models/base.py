import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, MetaData, func, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
    type_annotation_map: ClassVar[dict[type[datetime], DateTime]] = {
        datetime: DateTime(timezone=True)
    }

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {inspect(self).identity}>"


class UUIDPrimaryKeyMixin:
    uid: Mapped[uuid.UUID] = mapped_column("id", default=uuid.uuid7, primary_key=True)


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class TimestampMixin(CreatedAtMixin):
    __mapper_args__: ClassVar[dict[str, bool]] = {"eager_defaults": True}

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
