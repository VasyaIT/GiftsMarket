from enum import Enum, StrEnum, auto


COOKIES_MAX_AGE = 60 * 60 * 24 * 7


class OrderStatus(StrEnum):
    ON_MARKET = auto()
    BUY = auto()
    GIFT_TRANSFERRED = auto()
    GIFT_RECEIVED = auto()


class OrderType(Enum):
    COMMON = auto()
    VIP = auto()
    GIFT_TRANSFERRED = auto()
    GIFT_RECEIVED = auto()


class PriceList:
    UP_FOR_SALE = 0.5
    VIP_ORDER = 3
    PIN_VIP_ORDERS = 5
    PIN_COMMON_ORDERS = 3
    BUYER_FEE_TON = 0.1
    SELLER_FEE_PERCENT = 5
