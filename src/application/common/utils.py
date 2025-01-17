from random import randint

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from src.application.common.const import GIFT_RARITY_PERCENT, GiftRarity


def generate_deposit_comment(length: int = 8) -> str:
    return "".join(str(randint(0, 9)) for _ in range(length))


async def send_message(
    bot: Bot,
    message: str,
    chats_id: list[int] | list[str],
    parse_mode: str | None = "html",
    reply_markup: InlineKeyboardMarkup | None = None,
    message_thread_id: int | None = None
) -> None:
    for chat_id in chats_id:
        try:
            await bot.send_message(
                chat_id,
                message,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                message_thread_id=message_thread_id,
                disable_web_page_preview=True,
            )
        except TelegramAPIError:
            pass


async def send_photo(
    bot: Bot,
    photo: str,
    caption: str,
    chats_id: list[int] | list[str],
    parse_mode: str | None = "html",
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    for chat_id in chats_id:
        try:
            await bot.send_photo(
                chat_id, photo=photo, caption=caption, parse_mode=parse_mode, reply_markup=reply_markup
            )
        except TelegramAPIError:
            pass


async def is_subscriber(bot: Bot, channel_id: int | str, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(channel_id, user_id)
    except TelegramAPIError:
        return False
    return chat_member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)


def get_bot(token: str) -> Bot:
    return Bot(token=token, default=DefaultBotProperties(parse_mode="html"))


def calculate_gift_rarity(model_percent: float) -> GiftRarity:
    rarity = GiftRarity.LEGEND
    if model_percent >= GIFT_RARITY_PERCENT[GiftRarity.COMMON]:
        rarity = GiftRarity.COMMON
    elif model_percent >= GIFT_RARITY_PERCENT[GiftRarity.RARE]:
        rarity = GiftRarity.RARE
    elif model_percent >= GIFT_RARITY_PERCENT[GiftRarity.MYTHICAL]:
        rarity = GiftRarity.MYTHICAL
    return rarity


def build_direct_link(bot_username: str, parameter: str) -> str:
    return f"https://t.me/{bot_username}/store?startapp={parameter}"
