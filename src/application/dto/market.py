from pydantic import Field

from src.application.common.const import GiftRarity, GiftType
from src.application.dto.base import BaseDTO


class OrderIdDTO(BaseDTO):
    id: int


class CreateOrderDTO(BaseDTO):
    number: int = Field(ge=1, le=500000)
    image_url: str = Field(examples=["https://example.com"])
    type: GiftType
    price: float = Field(gt=0)
    is_vip: bool = False


class UpdateOrderDTO(BaseDTO):
    price: float = Field(gt=0)


class OrderDTO(CreateOrderDTO):
    image_url: str
