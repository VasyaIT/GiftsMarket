from datetime import datetime

from src.application.common.const import GiftRarity
from src.application.dto.base import BaseDTO


class CreateOrderDM(BaseDTO):
    gift_id: int
    seller_id: int
    number: int
    type: str
    model_name: str
    pattern_name: str
    background_name: str
    model: float
    pattern: float
    background: float
    rarity: GiftRarity
    is_active: bool


class OrderDM(CreateOrderDM):
    id: int
    buyer_id: int | None = None
    price: float
    completed_order_date: datetime | None = None
    is_vip: bool | None = None
    min_step: float | None = None
    auction_end_time: datetime | None = None


class ReadOrderDM(OrderDM):
    bids: list["ReadBidDM"]


class UserGiftDM(BaseDTO):
    id: int
    gift_id: int
    type: str
    number: int
    model: float
    pattern: float
    background: float
    model_name: str
    pattern_name: str
    background_name: str
    rarity: GiftRarity
    is_active: bool
    price: float | None = None
    is_vip: bool | None = None
    min_step: float | None = None
    auction_end_time: datetime | None = None


class GiftFiltersDM(BaseDTO):
    limit: int | None
    offset: int | None
    from_price: float
    to_price: float
    from_gift_number: int
    to_gift_number: int
    rarities: list[GiftRarity]
    types: list[str] | None
    model_names: list[str] | None
    user_id: int


class BidDM(BaseDTO):
    amount: float
    gift_id: int
    buyer_id: int


class ReadBidDM(BaseDTO):
    amount: float
    created_at: datetime


class BidSuccessDM(BaseDTO):
    user_balance: float
    created_at: datetime
