from pydantic import BaseModel

from src.application.common.const import GiftType, HistoryType


class CreateHistoryDM(BaseModel):
    type: HistoryType
    price: float
    stars: int | None = None
    gift: GiftType | None = None
    user_id: int


class HistoryDM(CreateHistoryDM):
    id: int
