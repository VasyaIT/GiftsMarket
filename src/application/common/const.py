from enum import Enum, StrEnum, auto


MINUTES_TO_SEND_GIFT = 20


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
    PIN_VIP_ORDERS = 5
    PIN_COMMON_ORDERS = 3
    BUYER_FEE_TON = 0.1
    SELLER_FEE_PERCENT = 1
    REFERRAL_PERCENT = 40
    VIP_REFERRAL_PERCENT = 50


class GiftType(Enum):
    DUROV_CAP = "durov_cap"
    SIGNET_RING = "signet_ring"
    PLUSH_PEPE = "plush_pepe"
    PERFUME_BOTTLE = "perfume_bottle"
    SPY_AGARIC = "spy_agaric"
    SHARP_TONGUE = "sharp_tongue"
    SCARED_CAT = "scared_cat"
    HEX_POT = "hex_pot"
    KISSED_FROG = "kissed_frog"
    SANTA_HAT = "santa_hat"
    HOMEMADE_CAKE = "homemade_cake"
    SKULL_FLOWER = "skull_flower"
    PRECIOUS_PEACH = "precious_peach"
    SPICED_WINE = "spiced_wine"
    JELLY_BUNNY = "jelly_bunny"
    ETERNAL_ROSE = "eternal_rose"
    BERRY_BOX = "berry_box"
    VINTAGE_CIGAR = "vintage_cigar"
    MAGIC_POTION = "magic_potion"
    EVIL_EYE = "evil_eye"
    TRAPPED_HEART = "trapped_heart"


GIFT_RARITY_PERCENT = {
    GiftRarity.COMMON: 2.5, GiftRarity.RARE: 1.7, GiftRarity.MYTHICAL: 0.7, GiftRarity.LEGEND: 0
}
