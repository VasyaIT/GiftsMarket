from pydantic import BaseModel

from src.application.common.const import OrderStatus


class StarOrderDM(BaseModel):
    amount: float
    price: float
    seller_id: int
    buyer_id: int | None
    status: OrderStatus


class CreateStarOrderDM(BaseModel):
    amount: float
    price: float
    seller_id: int
