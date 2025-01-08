from traceback import format_exc

from aiogram import Bot
from aiogram.utils.markdown import hpre
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.application.common.utils import send_message
from src.entrypoint.config import BotConfig, Config


def setup_middlewares(app: FastAPI, config: Config, bot: Bot) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.app.cors_allowed_origins,
        allow_methods=["OPTIONS", "GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
        allow_credentials=True
    )
    app.add_middleware(HandleExceptionMiddleware, bot, config.bot)


class HandleExceptionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, bot, bot_config: BotConfig) -> None:
        super().__init__(app)
        self._bot = bot
        self._bot_config = bot_config

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception:
            message = f"{format_exc(chain=False)[1800:1800 + 4096]}"
            await send_message(self._bot, hpre(message), self._bot_config.owners_chat_id)
            raise
