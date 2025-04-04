from fastapi import FastAPI

from src.presentation.api.giveaway.router import giveaway_router
from src.presentation.api.history.router import history_router
from src.presentation.api.market.router import market_router
from src.presentation.api.star.router import star_router
from src.presentation.api.user.router import user_router
from src.presentation.api.wallet.router import wallet_router


def setup_routers(app: FastAPI) -> None:
    app.include_router(user_router)
    app.include_router(market_router)
    app.include_router(giveaway_router)
    app.include_router(wallet_router)
    app.include_router(history_router)
    app.include_router(star_router)
