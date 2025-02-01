from src.application.common.const import GiftType
from src.application.dto.common import GiftImagesDTO


def get_gift_images(webapp_url: str) -> GiftImagesDTO:
    data = {
        GiftType.SANTA_HAT: [
            f"{webapp_url}/images/{GiftType.SANTA_HAT.value}/{GiftType.SANTA_HAT.value}_{number}.json"
            for number in range(1, 70)
        ],
        GiftType.SIGNET_RING: [
            f"{webapp_url}/images/{GiftType.SIGNET_RING.value}/{GiftType.SIGNET_RING.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.PRECIOUS_PEACH: [
            f"{webapp_url}/images/{GiftType.PRECIOUS_PEACH.value}/{GiftType.PRECIOUS_PEACH.value}_{number}.json"
            for number in range(1, 81)
        ],
        GiftType.PLUSH_PEPE: [
            f"{webapp_url}/images/{GiftType.PLUSH_PEPE.value}/{GiftType.PLUSH_PEPE.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.SPICED_WINE: [
            f"{webapp_url}/images/{GiftType.SPICED_WINE.value}/{GiftType.SPICED_WINE.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.JELLY_BUNNY: [
            f"{webapp_url}/images/{GiftType.JELLY_BUNNY.value}/{GiftType.JELLY_BUNNY.value}_{number}.json"
            for number in range(1, 100)
        ],
        GiftType.DUROV_CAP: [
            f"{webapp_url}/images/{GiftType.DUROV_CAP.value}/{GiftType.DUROV_CAP.value}_{number}.json"
            for number in range(1, 56)
        ],
        GiftType.PERFUME_BOTTLE: [
            f"{webapp_url}/images/{GiftType.PERFUME_BOTTLE.value}/{GiftType.PERFUME_BOTTLE.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.ETERNAL_ROSE: [
            f"{webapp_url}/images/{GiftType.ETERNAL_ROSE.value}/{GiftType.ETERNAL_ROSE.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.BERRY_BOX: [
            f"{webapp_url}/images/{GiftType.BERRY_BOX.value}/{GiftType.BERRY_BOX.value}_{number}.json"
            for number in range(1, 71)
        ],
        GiftType.VINTAGE_CIGAR: [
            f"{webapp_url}/images/{GiftType.VINTAGE_CIGAR.value}/{GiftType.VINTAGE_CIGAR.value}_{number}.json"
            for number in range(1, 56)
        ],
        GiftType.MAGIC_POTION: [
            f"{webapp_url}/images/{GiftType.MAGIC_POTION.value}/{GiftType.MAGIC_POTION.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.KISSED_FROG: [
            f"{webapp_url}/images/{GiftType.KISSED_FROG.value}/{GiftType.KISSED_FROG.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.HEX_POT: [
            f"{webapp_url}/images/{GiftType.HEX_POT.value}/{GiftType.HEX_POT.value}_{number}.json"
            for number in range(1, 81)
        ],
        GiftType.EVIL_EYE: [
            f"{webapp_url}/images/{GiftType.EVIL_EYE.value}/{GiftType.EVIL_EYE.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.SHARP_TONGUE: [
            f"{webapp_url}/images/{GiftType.SHARP_TONGUE.value}/{GiftType.SHARP_TONGUE.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.TRAPPED_HEART: [
            f"{webapp_url}/images/{GiftType.TRAPPED_HEART.value}/{GiftType.TRAPPED_HEART.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.SKULL_FLOWER: [
            f"{webapp_url}/images/{GiftType.SKULL_FLOWER.value}/{GiftType.SKULL_FLOWER.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.SCARED_CAT: [
            f"{webapp_url}/images/{GiftType.SCARED_CAT.value}/{GiftType.SCARED_CAT.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.SPY_AGARIC: [
            f"{webapp_url}/images/{GiftType.SPY_AGARIC.value}/{GiftType.SPY_AGARIC.value}_{number}.json"
            for number in range(1, 81)
        ],
        GiftType.HOMEMADE_CAKE: [
            f"{webapp_url}/images/{GiftType.HOMEMADE_CAKE.value}/{GiftType.HOMEMADE_CAKE.value}_{number}.json"
            for number in range(1, 100)
        ],
        GiftType.LUNAR_SNAKE: [
            f"{webapp_url}/images/{GiftType.LUNAR_SNAKE.value}/{GiftType.LUNAR_SNAKE.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.PARTY_SPARKLER: [
            f"{webapp_url}/images/{GiftType.PARTY_SPARKLER.value}/{GiftType.PARTY_SPARKLER.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.JESTER_HAT: [
            f"{webapp_url}/images/{GiftType.JESTER_HAT.value}/{GiftType.JESTER_HAT.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.GENIE_LAMP: [
            f"{webapp_url}/images/{GiftType.GENIE_LAMP.value}/{GiftType.GENIE_LAMP.value}_{number}.json"
            for number in range(1, 50)
        ],
        GiftType.WITCH_HAT: [
            f"{webapp_url}/images/{GiftType.WITCH_HAT.value}/{GiftType.WITCH_HAT.value}_{number}.json"
            for number in range(1, 89)
        ],
        GiftType.COOKIE_HEART: [
            f"{webapp_url}/images/{GiftType.COOKIE_HEART.value}/{GiftType.COOKIE_HEART.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.ETERNAL_CANDLE: [
            f"{webapp_url}/images/{GiftType.ETERNAL_CANDLE.value}/{GiftType.ETERNAL_CANDLE.value}_{number}.json"
            for number in range(1, 81)
        ],
        GiftType.HANGING_STAR: [
            f"{webapp_url}/images/{GiftType.HANGING_STAR.value}/{GiftType.HANGING_STAR.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.JINGLE_BELLS: [
            f"{webapp_url}/images/{GiftType.JINGLE_BELLS.value}/{GiftType.JINGLE_BELLS.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.CRYSTAL_BALL: [
            f"{webapp_url}/images/{GiftType.CRYSTAL_BALL.value}/{GiftType.CRYSTAL_BALL.value}_{number}.json"
            for number in range(1, 56)
        ],
        GiftType.SWISS_WATCH: [
            f"{webapp_url}/images/{GiftType.SWISS_WATCH.value}/{GiftType.SWISS_WATCH.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.DESK_CALENDAR: [
            f"{webapp_url}/images/{GiftType.DESK_CALENDAR.value}/{GiftType.DESK_CALENDAR.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.FLYING_BROOM: [
            f"{webapp_url}/images/{GiftType.FLYING_BROOM.value}/{GiftType.FLYING_BROOM.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.HYPNO_LOLLIPOP: [
            f"{webapp_url}/images/{GiftType.HYPNO_LOLLIPOP.value}/{GiftType.HYPNO_LOLLIPOP.value}_{number}.json"
            for number in range(1, 101)
        ],
        GiftType.LOVE_CANDLE: [
            f"{webapp_url}/images/{GiftType.LOVE_CANDLE.value}/{GiftType.LOVE_CANDLE.value}_{number}.json"
            for number in range(1, 51)
        ],
        GiftType.SNOW_MITTENS: [
            f"{webapp_url}/images/{GiftType.SNOW_MITTENS.value}/{GiftType.SNOW_MITTENS.value}_{number}.json"
            for number in range(1, 101)
        ],
    }
    return GiftImagesDTO(data=data)
