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
    await message.answer_photo("https://cache.tonapi.io/imgproxy/4BLBr1L19wTbS6I_cUPzaZPrrW2THEtOaF1xVERbU_Y/rs:fill:1500:1500:1/g:no/aHR0cHM6Ly9zdGF0aWMuc3Rvbi5maS9mYXJtLW5mdC9TdG9uX0Zhcm1fTkZULnBuZw.webp")
