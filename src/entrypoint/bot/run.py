from aiogram import Dispatcher

from src.application.common.utils import get_bot
from src.entrypoint.config import Config
from src.presentation.bot.handlers.base import router


async def start_bot() -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    dp = Dispatcher(config=config)
    dp.include_routers(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
