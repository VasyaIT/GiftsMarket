from pydantic import Field

from src.application.dto.base import BaseDTO


class OrderIdDTO(BaseDTO):
    id: int


class CreateOrderDTO(BaseDTO):
    gift_id: int
    price: int = Field(ge=1, le=500000)
    is_vip: bool = False


class UpdateOrderDTO(BaseDTO):
    price: float = Field(gt=0)
