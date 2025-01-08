from enum import Enum, StrEnum, auto


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
    UP_FOR_SALE = 0.5
    VIP_ORDER = 3
    PIN_VIP_ORDERS = 5
    PIN_COMMON_ORDERS = 3
    BUYER_FEE_TON = 0.1
    SELLER_FEE_PERCENT = 5
    REFERRAL_PERCENT = 20
    VIP_REFERRAL_PERCENT = 40


class GiftType(Enum):
    DUROV_CAP = "Durov's Cap"
    SIGNET_RING = "Signet Ring"
    PLUSH_PEPE = "Plush Pepe"
    PERFUME_BOTTLE = "Perfume Bottle"
    SPY_AGARIC = "Spy Agaric"
    SHARP_TONGUE = "Sharp Tongue"
    SCARED_CAT = "Scared Cat"
    HEX_POT = "Hex Pot"
    KISSED_FROG = "Kissed Frog"
    SANTA_HAT = "Santa Hat"
    HOMEMADE_CAKE = "Homemade Cake"
    SKULL_FLOWER = "Skull Flower"
    PRECIOUS_PEACH = "Precious Peach"
    SPICED_WINE = "Spiced Wine"
    JELLY_BUNNY = "Jelly Bunny"
    ETERNAL_ROSE = "Eternal Rose"
    BERRY_BOX = "Berry Box"
    VINTAGE_CIGAR = "Vintage Cigar"
    MAGIC_POTION = "Magic Potion"
    EVIL_EYE = "Evil Eye"
