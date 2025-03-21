from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.application.common.const import GiftRarity, GiftType
from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User


class Order(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    number: Mapped[int] = mapped_column(Integer)
    type: Mapped[GiftType] = mapped_column(ENUM(GiftType))
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    model: Mapped[float] = mapped_column(Float)
    pattern: Mapped[float] = mapped_column(Float)
    background: Mapped[float] = mapped_column(Float)
    model_name: Mapped[str] = mapped_column(String)
    pattern_name: Mapped[str] = mapped_column(String)
    background_name: Mapped[str] = mapped_column(String)
    rarity: Mapped[GiftRarity] = mapped_column(ENUM(GiftRarity))
    completed_order_date: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    min_step: Mapped[float | None] = mapped_column(Float, nullable=True)
    auction_end_time: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vip: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    buyer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    seller: Mapped[User] = relationship("User", lazy="selectin", foreign_keys="Order.seller_id")
    buyer: Mapped[User] = relationship("User", lazy="selectin", foreign_keys="Order.buyer_id")
