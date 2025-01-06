from fastapi import Query

from src.application.common.const import GiftRarity, GiftType, OrderType


class GiftFilterParams:
    def __init__(
        self,
        offset: int | None = Query(default=None, ge=0),
        limit: int | None = Query(default=50, ge=0, le=1000),
        from_price: float | None = Query(default=None, ge=0),
        to_price: float | None = Query(default=None, ge=0),
        rarity: list[GiftRarity] | None = Query(default=None),
        type: list[GiftType] | None = Query(default=None),
    ) -> None:
        self.offset = offset
        self.limit = limit
        self.from_price = from_price
        self.to_price = to_price
        self.rarities = rarity
        self.types = type


class OrderFilterParams:
    def __init__(
        self,
        offset: int | None = Query(default=None, ge=0),
        limit: int | None = Query(default=50, ge=0, le=1000),
        order_type: OrderType = Query(default=OrderType.ALL),
    ) -> None:
        self.offset = offset
        self.limit = limit
        self.order_type = order_type
