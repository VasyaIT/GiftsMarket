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
    SELLER_FEE_PERCENT = 5
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
    GiftRarity.COMMON: 2, GiftRarity.RARE: 1, GiftRarity.MYTHICAL: 0.6, GiftRarity.LEGEND: 0
}

GIFT_TYPE_MAP = {
    "Santa Hat": GiftType.SANTA_HAT,
    "Signet Ring": GiftType.SIGNET_RING,
    "Precious Peach": GiftType.PRECIOUS_PEACH,
    "Plush Pepe": GiftType.PLUSH_PEPE,
    "Spiced Wine": GiftType.SPICED_WINE,
    "Jelly Bunny": GiftType.JELLY_BUNNY,
    "Durov's Cap": GiftType.DUROV_CAP,
    "Perfume Bottle": GiftType.PERFUME_BOTTLE,
    "Eternal Rose": GiftType.ETERNAL_ROSE,
    "Berry Box": GiftType.BERRY_BOX,
    "Vintage Cigar": GiftType.VINTAGE_CIGAR,
    "Magic Potion": GiftType.MAGIC_POTION,
    "Kissed Frog": GiftType.KISSED_FROG,
    "Hex Pot": GiftType.HEX_POT,
    "Evil Eye": GiftType.EVIL_EYE,
    "Sharp Tongue": GiftType.SHARP_TONGUE,
    "Trapped Heart": GiftType.TRAPPED_HEART,
    "Skull Flower": GiftType.SKULL_FLOWER,
    "Scared Cat": GiftType.SCARED_CAT,
    "Spy Agaric": GiftType.SPY_AGARIC,
    "Homemade Cake": GiftType.HOMEMADE_CAKE,
}
