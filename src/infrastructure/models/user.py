from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
