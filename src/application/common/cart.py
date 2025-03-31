from src.application.dto.base import BaseDTO
from src.domain.entities.cart import CartGiftDM


class CartGiftDTO(BaseDTO):
    id: int
    price: float


class ResponseCartDTO(BaseDTO):
    success: bool
    cart: list[CartGiftDM]
