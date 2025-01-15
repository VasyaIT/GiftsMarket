from datetime import datetime

from sqlalchemy import TIMESTAMP, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.application.common.const import OrderStatus
from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User


class Star(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    price: Mapped[float] = mapped_column(Float)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[OrderStatus] = mapped_column(ENUM(OrderStatus), default=OrderStatus.ON_MARKET)
    created_order_date: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    completed_order_date: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    buyer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    seller: Mapped[User] = relationship(
        "User", lazy="selectin", foreign_keys="Order.seller_id"
    )
    buyer: Mapped[User] = relationship("User", lazy="selectin", foreign_keys="Order.buyer_id")
