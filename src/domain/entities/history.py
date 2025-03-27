from datetime import datetime

from src.application.common.const import HistoryType
from src.application.dto.base import BaseDTO


class CreateHistoryDM(BaseDTO):
    type: HistoryType
    price: float
    stars: int | None = None
    gift: str | None = None
    gift_number: int | None = None
    model_name: str | None = None
    user_id: int


class HistoryDM(CreateHistoryDM):
    id: int
    created_at: datetime


class ActivityDM(CreateHistoryDM):
    id: int
    created_at: datetime
    type: HistoryType
    price: float
    stars: int | None = None
    gift: str | None = None
    gift_number: int | None = None
    model_name: str | None = None
