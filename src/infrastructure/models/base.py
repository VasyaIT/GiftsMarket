from datetime import datetime
from re import sub

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "s"
