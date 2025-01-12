from datetime import datetime

from pydantic import BaseModel

from src.application.common.const import GiftRarity, GiftType, OrderStatus


class CharacteristicsOrderDM(BaseModel):
    model: float
    pattern: float
    background: float
    rarity: GiftRarity
    is_active: bool


class UpdateOrderDM(BaseModel):
    price: float


class CreateOrderDM(BaseModel):
    number: int
    image_url: str
    type: GiftType
    price: float
    seller_id: int


class OrderDM(CreateOrderDM):
    id: int
    buyer_id: int | None
    status: OrderStatus
    created_order_date: datetime | None
    completed_order_date: datetime | None


class ReadOrderDM(CreateOrderDM):
    status: OrderStatus
    created_order_date: datetime | None
    completed_order_date: datetime | None
    created_at: datetime
    model: float | None
    pattern: float | None
    background: float | None
    rarity: GiftRarity | None
    buyer_id: int | None
    seller_name: str | None
    buyer_name: str | None
    id: int


class UserGiftsDM(BaseModel):
    id: int
    image_url: str
    type: GiftType
    number: int
    price: float
    model: float | None
    pattern: float | None
    background: float | None
    rarity: GiftRarity | None
    is_active: bool


class GetUserGiftsDM(BaseModel):
    user_id: int
    status: OrderStatus


class GiftFiltersDM(BaseModel):
    limit: int | None
    offset: int | None
    from_price: float
    to_price: float
    rarities: list[GiftRarity]
    types: list[GiftType]
    status: OrderStatus
    user_id: int


class OrderFiltersDM(BaseModel):
    limit: int | None
    offset: int | None
    statuses: list[OrderStatus]
    user_id: int
    is_buyer: bool
    is_seller: bool
