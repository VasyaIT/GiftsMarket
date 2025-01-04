from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.application.common.const import OrderStatus
from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User


class Order(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    buyer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(ENUM(OrderStatus), default=OrderStatus.ON_MARKET)

    seller: Mapped[User] = relationship(
        "User", lazy="selectin", foreign_keys="Order.seller_id"
    )
    buyer: Mapped[User] = relationship("User", lazy="selectin", foreign_keys="Order.buyer_id")
