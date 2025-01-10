from aiogram import Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo

from src.application.common.utils import get_bot
from src.entrypoint.config import Config
from src.presentation.bot.handlers.base import router


async def start_bot() -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    dp = Dispatcher(config=config, bot=bot)
    dp.include_routers(router)
    menu_button = MenuButtonWebApp(text="Store", web_app=WebAppInfo(url=config.bot.WEBAPP_URL))
    await bot.set_chat_menu_button(menu_button=menu_button)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
