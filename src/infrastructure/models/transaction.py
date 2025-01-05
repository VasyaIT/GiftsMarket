from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base import Base


class Lt(Base):
    last_lt: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)


class WithdrawRequest(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float)
    wallet: Mapped[str] = mapped_column(String)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
