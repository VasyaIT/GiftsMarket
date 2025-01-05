from pydantic import BaseModel

from src.application.common.const import GiftRarity, GiftType, OrderStatus


class CreateOrderDM(BaseModel):
    image_url: str
    type: GiftType
    price: float
    model: float
    pattern: float
    background: float
    rarity: GiftRarity
    seller_id: int


class OrderDM(CreateOrderDM):
    id: int
    buyer_id: int | None
    status: OrderStatus


class UpdateOrderStatusDM(BaseModel):
    id: int
    old_status: OrderStatus
    new_status: OrderStatus
    buyer_id: int | None = None


class OrderFiltersDM(BaseModel):
    limit: int | None
    offset: int | None
    from_price: float
    to_price: float
    rarities: list[GiftRarity]
    types: list[GiftType]
    status: OrderStatus
