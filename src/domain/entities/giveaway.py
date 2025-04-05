from datetime import datetime

from pydantic import BaseModel

from src.application.common.const import GiveawayType


class TelegramChannelDM(BaseModel):
    id: int
    title: str
    username: str
    image_url: str


class CreateGiveawayDM(BaseModel):
    type: GiveawayType
    gifts_ids: list[int]
    channels_usernames: list[str]
    quantity_members: int
    end_time: datetime
    price: float
    participants_ids: list[int] = []

    user_id: int


class GiveawayDM(CreateGiveawayDM):
    id: int
