from pydantic import BaseModel

from src.application.common.const import OrderStatus


class CreateOrderDM(BaseModel):
    image_url: str
    title: str
    amount: float
    seller_id: int


class OrderDM(BaseModel):
    id: int
    image_url: str
    title: str
    amount: float
    seller_id: int
    buyer_id: int | None
    status: OrderStatus
