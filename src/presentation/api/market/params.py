from enum import StrEnum, auto

from fastapi import Query

from src.application.common.const import GiftRarity, GiftType


class GiftFilterParams:
    def __init__(
        self,
        offset: int | None = Query(default=None, ge=0),
        limit: int | None = Query(default=50, ge=0, le=1000),
        from_price: float | None = Query(default=None, ge=0),
        to_price: float | None = Query(default=None, ge=0),
        from_gift_number: int | None = Query(default=1, gt=0),
        to_gift_number: int | None = Query(default=None, gt=0),
        rarity: list[GiftRarity] | None = Query(default=None, alias="rarity[]"),
        type: list[GiftType] | None = Query(default=None, alias="type[]"),
    ) -> None:
        self.offset = offset
        self.limit = limit
        self.from_price = from_price
        self.to_price = to_price
        self.from_gift_number = from_gift_number
        self.to_gift_number = to_gift_number
        self.rarities = rarity
        self.types = type


class GiftSortParams(StrEnum):
    PRICE_LOW_TO_HIGH = auto()
    PRICE_HIGH_TO_LOW = auto()
    RECENTLY_ADDED = auto()
    OLDEST = auto()
