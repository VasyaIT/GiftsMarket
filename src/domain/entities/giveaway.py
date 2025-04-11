from datetime import datetime

from pydantic import BaseModel

from src.application.common.const import GiveawayType
from src.domain.entities.market import UserGiftDM


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
    winners_ids: list[int] = []
    referrers_ids: list[int] = []

    user_id: int


class GiveawayDM(CreateGiveawayDM):
    id: int


class FullGiveawayDM(GiveawayDM):
    gifts: list[UserGiftDM]
    channels: list[TelegramChannelDM]


class GiveawayParticipantDM(BaseModel):
    photo_url: str
    name: str | None
    chance_win: float
    count_referrals: int
    is_win: bool
