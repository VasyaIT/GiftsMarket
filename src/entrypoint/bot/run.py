from aiogram import Dispatcher

from src.application.common.utils import get_bot
from src.entrypoint.config import Config
from src.presentation.bot.handlers.base import router
from src.presentation.bot.handlers.inline import inline_router


async def start_bot() -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    bot_username = (await bot.get_me()).username
    dp = Dispatcher(config=config, bot=bot, bot_username=bot_username)
    dp.include_routers(router, inline_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
