from enum import StrEnum, auto

from fastapi import Query

from src.application.common.const import GiftRarity, ShopType


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
        type: list[str] | None = Query(default=None, alias="type[]"),
        model_name: list[str] | None = Query(default=None, alias="model_name[]"),
        shop_type: ShopType | None = Query(default=ShopType.MARKET),
    ) -> None:
        self.offset = offset
        self.limit = limit
        self.from_price = from_price
        self.to_price = to_price
        self.from_gift_number = from_gift_number
        self.to_gift_number = to_gift_number
        self.rarities = rarity
        self.types = type
        self.model_names = model_name
        self.shop_type = shop_type


class GiftSortParams(StrEnum):
    PRICE_LOW_TO_HIGH = auto()
    PRICE_HIGH_TO_LOW = auto()
    RECENTLY_ADDED = auto()
    OLDEST = auto()
