from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base import Base


class Lt(Base):
    last_lt: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
