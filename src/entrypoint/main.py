from aiogram import Bot
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from pyrogram.client import Client

from src.application.common.utils import get_bot
from src.entrypoint.config import Config
from src.entrypoint.ioc import AppProvider
from src.presentation.api.middlewares import setup_middlewares
from src.presentation.api.routers import setup_routers
from src.presentation.client.handlers.setup import setup_client_handlers


def get_fastapi_app() -> FastAPI:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    client = Client("client", config.bot.API_ID, config.bot.API_HASH, workdir="src")
    setup_client_handlers(client)

    async def on_startup() -> None:
        await client.start()

    async def on_shutdown() -> None:
        await bot.session.close()
        await client.stop()

    app = FastAPI(
        debug=config.app.DEBUG,
        docs_url=config.app.docs_url,
        openapi_url=config.app.openapi_url,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
    )
    container = make_async_container(AppProvider(), context={Config: config, Bot: bot, Client: client})
    setup_dishka(container, app)
    setup_middlewares(app, config, bot)
    setup_routers(app)
    return app
