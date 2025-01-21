from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User


class Auction(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_bid: Mapped[float] = mapped_column(Float, default=0)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    buyer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    owner: Mapped[User] = relationship(
        "User", lazy="selectin", foreign_keys="Auction.seller_id"
    )
    buyer: Mapped[User] = relationship("User", lazy="selectin", foreign_keys="Auction.buyer_id")
