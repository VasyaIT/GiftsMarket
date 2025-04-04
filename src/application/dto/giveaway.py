from datetime import datetime

from pydantic import Field

from src.application.common.const import GiveawayType
from src.application.dto.base import BaseDTO


class CreateGiveawayDTO(BaseDTO):
    type: GiveawayType
    gifts_ids: list[int]
    channels_usernames: list[str]
    quantity_members: int
    end_time: datetime
    price: float = Field(ge=0)
