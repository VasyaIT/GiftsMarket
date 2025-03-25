from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.application.common.const import GiftType, HistoryType
from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User


class History(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[HistoryType] = mapped_column(ENUM(HistoryType))
    price: Mapped[float] = mapped_column(Float)
    stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gift: Mapped[GiftType | None] = mapped_column(ENUM(GiftType), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped[User] = relationship("User", lazy="selectin")
