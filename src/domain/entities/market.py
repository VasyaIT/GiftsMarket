from datetime import datetime

from pydantic import BaseModel

from src.application.common.const import GiftRarity, GiftType


class CreateOrderDM(BaseModel):
    id: int
    seller_id: int
    number: int
    type: GiftType
    model_name: str
    pattern_name: str
    background_name: str
    model: float
    pattern: float
    background: float
    rarity: GiftRarity
    is_active: bool


class OrderDM(CreateOrderDM):
    buyer_id: int | None = None
    price: float = 0
    completed_order_date: datetime | None = None
    is_vip: bool | None = None


class UserGiftDM(BaseModel):
    id: int
    type: GiftType
    number: int
    model: float
    pattern: float
    background: float
    model_name: str
    pattern_name: str
    background_name: str
    rarity: GiftRarity


class GiftFiltersDM(BaseModel):
    limit: int | None
    offset: int | None
    from_price: float
    to_price: float
    from_gift_number: int
    to_gift_number: int
    rarities: list[GiftRarity]
    types: list[GiftType]
    user_id: int
