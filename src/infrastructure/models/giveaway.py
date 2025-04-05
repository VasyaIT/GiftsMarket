from datetime import datetime

from sqlalchemy import TIMESTAMP, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.application.common.const import GiveawayType
from src.infrastructure.models.base import Base
from src.infrastructure.models.user import User


class Giveaway(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[GiveawayType] = mapped_column(ENUM(GiveawayType))
    price: Mapped[float] = mapped_column(Float)
    gifts_ids: Mapped[list[int]] = mapped_column(JSONB)
    channels_usernames: Mapped[list[str]] = mapped_column(JSONB)
    quantity_members: Mapped[int] = mapped_column(Integer)
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped[User] = relationship("User", lazy="selectin")
