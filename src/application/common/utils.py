from random import randint

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


def generate_deposit_comment(length: int = 8) -> str:
    return "".join(str(randint(0, 9)) for _ in range(length))


async def send_message(
    bot: Bot, message: str, chats_id: list[int] | list[str], parse_mode: str | None = "html"
) -> None:
    for chat_id in chats_id:
        await bot.send_message(chat_id, message, parse_mode=parse_mode, disable_web_page_preview=True)


def get_bot(token: str) -> Bot:
    return Bot(token=token, default=DefaultBotProperties(parse_mode="html"))
