from datetime import datetime

from pydantic import BaseModel

from src.application.common.const import OrderStatus


class StarOrderDM(BaseModel):
    amount: float
    price: float
    seller_id: int
    buyer_id: int | None
    status: OrderStatus
    created_order_date: datetime | None
    completed_order_date: datetime | None
    created_at: datetime


class CreateStarOrderDM(BaseModel):
    amount: float
    price: float
    seller_id: int
