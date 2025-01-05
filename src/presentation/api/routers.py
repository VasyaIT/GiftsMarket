from fastapi import FastAPI

from src.presentation.api.deposit.router import deposit_router
from src.presentation.api.market.router import market_router
from src.presentation.api.user.router import user_router


def setup_routers(app: FastAPI) -> None:
    app.include_router(user_router)
    app.include_router(market_router)
    app.include_router(deposit_router)
