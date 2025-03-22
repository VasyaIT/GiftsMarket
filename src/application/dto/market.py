from datetime import datetime

from pydantic import Field

from src.application.dto.base import BaseDTO


class OrderIdDTO(BaseDTO):
    id: int


class CreateOrderDTO(BaseDTO):
    gift_id: int
    price: float = Field(ge=0.1, le=999999)
    is_vip: bool = False
    min_step: float | None = Field(default=None, ge=0.1, le=999999)
    auction_end_time: datetime | None = None


class UpdateOrderDTO(BaseDTO):
    price: float = Field(ge=0.1, le=999999)


class BidDTO(BaseDTO):
    id: int
    amount: float = Field(ge=0.1, le=999999)
