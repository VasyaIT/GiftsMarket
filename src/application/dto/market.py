from src.application.dto.base import BaseDTO


class CreateOrderDTO(BaseDTO):
    title: str
    amount: float


class OrderIdDTO(BaseDTO):
    id: int
