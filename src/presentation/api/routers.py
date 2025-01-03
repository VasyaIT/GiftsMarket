from fastapi import FastAPI

from src.presentation.api.user.router import user_router


def setup_routers(app: FastAPI) -> None:
    app.include_router(user_router)
