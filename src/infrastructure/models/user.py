from sqlalchemy import BigInteger, Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    deposit_comment: Mapped[str] = mapped_column(String, unique=True)
    balance: Mapped[float] = mapped_column(Float, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
