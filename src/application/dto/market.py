from src.application.common.const import GiftRarity, GiftType
from src.application.dto.base import BaseDTO


class CreateOrderDTO(BaseDTO):
    type: GiftType
    price: float
    model: float
    pattern: float
    background: float


class OrderIdDTO(BaseDTO):
    id: int


class OrderDTO(OrderIdDTO, CreateOrderDTO):
    image_url: str
    rarity: GiftRarity
