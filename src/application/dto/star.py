from src.application.dto.base import BaseDTO


class CreateStarOrderDTO(BaseDTO):
    amount: int
    price: float
