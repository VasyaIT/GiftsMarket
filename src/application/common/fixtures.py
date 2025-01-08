from src.application.common.const import GiftType
from src.application.dto.common import GiftImagesDTO


def get_gift_images(webapp_url: str) -> GiftImagesDTO:
    data = {
        GiftType.SANTA_HAT: [
            f"{webapp_url}/images/{GiftType.SANTA_HAT.value}/{GiftType.SANTA_HAT.value}_{number}.webp"
            for number in range(1, 70)
        ],
        GiftType.SIGNET_RING: [
            f"{webapp_url}/images/{GiftType.SIGNET_RING.value}/{GiftType.SIGNET_RING.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.PRECIOUS_PEACH: [
            f"{webapp_url}/images/{GiftType.PRECIOUS_PEACH.value}/{GiftType.PRECIOUS_PEACH.value}_{number}.webp"
            for number in range(1, 81)
        ],
        GiftType.PLUSH_PEPE: [
            f"{webapp_url}/images/{GiftType.PLUSH_PEPE.value}/{GiftType.PLUSH_PEPE.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.SPICED_WINE: [
            f"{webapp_url}/images/{GiftType.SPICED_WINE.value}/{GiftType.SPICED_WINE.value}_{number}.webp"
            for number in range(1, 101)
        ],
        GiftType.JELLY_BUNNY: [
            f"{webapp_url}/images/{GiftType.JELLY_BUNNY.value}/{GiftType.JELLY_BUNNY.value}_{number}.webp"
            for number in range(1, 100)
        ],
        GiftType.DUROV_CAP: [
            f"{webapp_url}/images/{GiftType.DUROV_CAP.value}/{GiftType.DUROV_CAP.value}_{number}.webp"
            for number in range(1, 56)
        ],
        GiftType.PERFUME_BOTTLE: [
            f"{webapp_url}/images/{GiftType.PERFUME_BOTTLE.value}/{GiftType.PERFUME_BOTTLE.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.ETERNAL_ROSE: [
            f"{webapp_url}/images/{GiftType.ETERNAL_ROSE.value}/{GiftType.ETERNAL_ROSE.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.BERRY_BOX: [
            f"{webapp_url}/images/{GiftType.BERRY_BOX.value}/{GiftType.BERRY_BOX.value}_{number}.webp"
            for number in range(1, 71)
        ],
        GiftType.VINTAGE_CIGAR: [
            f"{webapp_url}/images/{GiftType.VINTAGE_CIGAR.value}/{GiftType.VINTAGE_CIGAR.value}_{number}.webp"
            for number in range(1, 56)
        ],
        GiftType.MAGIC_POTION: [
            f"{webapp_url}/images/{GiftType.MAGIC_POTION.value}/{GiftType.MAGIC_POTION.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.KISSED_FROG: [
            f"{webapp_url}/images/{GiftType.KISSED_FROG.value}/{GiftType.KISSED_FROG.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.HEX_POT: [
            f"{webapp_url}/images/{GiftType.HEX_POT.value}/{GiftType.HEX_POT.value}_{number}.webp"
            for number in range(1, 81)
        ],
        GiftType.EVIL_EYE: [
            f"{webapp_url}/images/{GiftType.EVIL_EYE.value}/{GiftType.EVIL_EYE.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.SHARP_TONGUE: [
            f"{webapp_url}/images/{GiftType.SHARP_TONGUE.value}/{GiftType.SHARP_TONGUE.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.TRAPPED_HEART: [
            f"{webapp_url}/images/{GiftType.TRAPPED_HEART.value}/{GiftType.TRAPPED_HEART.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.SKULL_FLOWER: [
            f"{webapp_url}/images/{GiftType.SKULL_FLOWER.value}/{GiftType.SKULL_FLOWER.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.SCARED_CAT: [
            f"{webapp_url}/images/{GiftType.SCARED_CAT.value}/{GiftType.SCARED_CAT.value}_{number}.webp"
            for number in range(1, 51)
        ],
        GiftType.SPY_AGARIC: [
            f"{webapp_url}/images/{GiftType.SPY_AGARIC.value}/{GiftType.SPY_AGARIC.value}_{number}.webp"
            for number in range(1, 81)
        ],
        GiftType.HOMEMADE_CAKE: [
            f"{webapp_url}/images/{GiftType.HOMEMADE_CAKE.value}/{GiftType.HOMEMADE_CAKE.value}_{number}.webp"
            for number in range(1, 100)
        ],
    }
    return GiftImagesDTO(data=data)
