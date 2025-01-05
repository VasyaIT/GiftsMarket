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


class ReadOrderDM(CreateOrderDM):
    image_url: str
    type: GiftType
    price: float
    model: float
    pattern: float
    background: float
    rarity: GiftRarity
    seller_name: str | None
    buyer_name: str | None


class UpdateOrderStatusDM(BaseModel):
    id: int
    current_status: OrderStatus
    new_status: OrderStatus
    current_buyer_id: int | None = None
    new_buyer_id: int | None = None


class GiftFiltersDM(BaseModel):
    limit: int | None
    offset: int | None
    from_price: float
    to_price: float
    rarities: list[GiftRarity]
    types: list[GiftType]
    status: OrderStatus


class OrderFiltersDM(BaseModel):
    limit: int | None
    offset: int | None
    statuses: list[OrderStatus]
