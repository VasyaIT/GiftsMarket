from pydantic import BaseModel


class CartGiftDM(BaseModel):
    id: int
    price: float
    seller_id: int
