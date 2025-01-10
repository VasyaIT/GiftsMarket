from pydantic import Field

from src.application.common.const import GiftRarity, GiftType
from src.application.dto.base import BaseDTO


class OrderIdDTO(BaseDTO):
    id: int


class CreateOrderDTO(BaseDTO):
    number: int
    image_url: str = Field(examples=["https://example.com"])
    type: GiftType
    price: float = Field(gt=0)
    model: float = Field(default=0, ge=0.01, le=5)
    pattern: float = Field(default=0, ge=0.01, le=5)
    background: float = Field(default=0, ge=0.01, le=5)


class OrderDTO(CreateOrderDTO):
    image_url: str
    rarity: GiftRarity
