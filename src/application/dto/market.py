from pydantic import Field, HttpUrl

from src.application.common.const import GiftRarity, GiftType
from src.application.dto.base import BaseDTO


class OrderIdDTO(BaseDTO):
    id: int


class CreateOrderDTO(OrderIdDTO):
    image_url: HttpUrl
    type: GiftType
    price: float = Field(ge=0)
    model: float = Field(default=0, ge=0, lt=100)
    pattern: float = Field(default=0, ge=0, lt=100)
    background: float = Field(default=0, ge=0, lt=100)


class OrderDTO(CreateOrderDTO):
    image_url: str
    rarity: GiftRarity
