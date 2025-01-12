from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.application.common.const import GiftRarity, GiftType, OrderStatus
from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User


class Order(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String)
    type: Mapped[GiftType] = mapped_column(ENUM(GiftType))
    price: Mapped[float] = mapped_column(Float)
    model: Mapped[float | None] = mapped_column(Float, nullable=True)
    pattern: Mapped[float | None] = mapped_column(Float, nullable=True)
    background: Mapped[float | None] = mapped_column(Float, nullable=True)
    rarity: Mapped[GiftRarity | None] = mapped_column(ENUM(GiftRarity), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(ENUM(OrderStatus), default=OrderStatus.ON_MARKET)
    created_order_date: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    completed_order_date: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    buyer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    seller: Mapped[User] = relationship(
        "User", lazy="selectin", foreign_keys="Order.seller_id"
    )
    buyer: Mapped[User] = relationship("User", lazy="selectin", foreign_keys="Order.buyer_id")

    __table_args__ = (
        UniqueConstraint('type', 'number', name='_type_number_uc'),
    )
