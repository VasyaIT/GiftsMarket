from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.entrypoint.config import BotConfig
from src.presentation.bot.keyboards.base import open_app_kb


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, bot_config: BotConfig) -> None:
    await message.answer(
        "🎁 <b>The best gift market in Telegram is already here!</b>\n\n"
        "🔥 Buy and sell gifts quickly and securely!",
        reply_markup=open_app_kb(bot_config.WEBAPP_URL)
    )
