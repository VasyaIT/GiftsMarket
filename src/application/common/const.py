from enum import Enum, StrEnum, auto


MINUTES_TO_SEND_GIFT = 20
MAX_GIFT_NUMBER = 500000
MAX_WITHDRAW_AMOUNT = 500
INLINE_IMAGE_URL = "https://store.nestdex.dev/media/inline_image.jpg"


class OrderStatus(StrEnum):
    ON_MARKET = auto()
    BUY = auto()
    SELLER_ACCEPT = auto()
    GIFT_TRANSFERRED = auto()
    GIFT_RECEIVED = auto()


class OrderType(StrEnum):
    ALL = auto()
    BUY = auto()
    SELL = auto()
    CLOSED = auto()


class GiftRarity(StrEnum):
    COMMON = auto()
    RARE = auto()
    MYTHICAL = auto()
    LEGEND = auto()


class PriceList:
    UP_FOR_SALE = 0.1
    VIP_ORDER = 3
    BUYER_FEE_TON = 0.1
    SELLER_FEE_PERCENT = 5
    REFERRAL_PERCENT = 25
    VIP_REFERRAL_PERCENT = 40
    CREATE_AUCTION = 20


class HistoryType(Enum):
    BUY_GIFT = "buy_gift"
    SELL_GIFT = "sell_gift"
    BID_GIFT = "bid_gift"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    BUY_STARS = "buy_stars"
    SELL_STARS = "sell_stars"


GIFT_RARITY_PERCENT = {
    GiftRarity.COMMON: 2,
    GiftRarity.RARE: 1,
    GiftRarity.MYTHICAL: 0.6,
    GiftRarity.LEGEND: 0,
}
