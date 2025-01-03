from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.entrypoint.config import Config
from src.entrypoint.ioc import AppProvider
from src.presentation.api.middlewares import setup_middlewares
from src.presentation.api.routers import setup_routers


def get_fastapi_app() -> FastAPI:
    config = Config()
    app = FastAPI(
        debug=config.app.DEBUG,
        docs_url=config.app.docs_url,
        openapi_url=config.app.openapi_url
    )
    container = make_async_container(AppProvider(), context={Config: config})
    setup_middlewares(app, config.app)
    setup_routers(app)
    setup_dishka(container, app)
    return app
