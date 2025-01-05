from fastapi import FastAPI

from src.presentation.api.market.router import market_router
from src.presentation.api.user.router import user_router
from src.presentation.api.wallet.router import wallet_router


def setup_routers(app: FastAPI) -> None:
    app.include_router(user_router)
    app.include_router(market_router)
    app.include_router(wallet_router)
