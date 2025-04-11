from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    photo_url: Mapped[str] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    deposit_comment: Mapped[str] = mapped_column(String, unique=True)
    balance: Mapped[float] = mapped_column(Float, default=0)
    commission: Mapped[float] = mapped_column(Float, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)


class UserReferral(Base):
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    referral_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    referrer: Mapped[User] = relationship(
        "User", lazy="selectin", foreign_keys="UserReferral.referrer_id"
    )
    referral: Mapped[User] = relationship(
        "User", lazy="selectin", foreign_keys="UserReferral.referral_id"
    )
