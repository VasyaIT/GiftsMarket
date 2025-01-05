from src.application.common.const import GiftType
from src.application.dto.base import BaseDTO


class CreateOrderDTO(BaseDTO):
    type: GiftType
    price: float
    model: float
    pattern: float
    background: float


class OrderIdDTO(BaseDTO):
    id: int
