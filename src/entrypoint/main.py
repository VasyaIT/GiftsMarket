from aiogram import Bot
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.application.common.utils import get_bot
from src.entrypoint.config import Config
from src.entrypoint.ioc import AppProvider
from src.presentation.api.middlewares import setup_middlewares
from src.presentation.api.routers import setup_routers


def get_fastapi_app() -> FastAPI:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)

    async def on_shutdown() -> None:
        await bot.session.close()

    app = FastAPI(
        debug=config.app.DEBUG,
        docs_url=config.app.docs_url,
        openapi_url=config.app.openapi_url,
        on_shutdown=[on_shutdown],
    )
    container = make_async_container(AppProvider(), context={Config: config, Bot: bot})
    setup_dishka(container, app)
    setup_middlewares(app, config.app)
    setup_routers(app)
    return app
