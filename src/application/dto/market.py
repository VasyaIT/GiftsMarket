from pydantic import Field

from src.application.common.const import GiftRarity, GiftType
from src.application.dto.base import BaseDTO


class CreateOrderDTO(BaseDTO):
    type: GiftType
    price: float = Field(ge=0)
    model: float = Field(default=0, ge=0, lt=100)
    pattern: float = Field(default=0, ge=0, lt=100)
    background: float = Field(default=0, ge=0, lt=100)


class OrderIdDTO(BaseDTO):
    id: int


class OrderDTO(OrderIdDTO, CreateOrderDTO):
    image_url: str
    rarity: GiftRarity
