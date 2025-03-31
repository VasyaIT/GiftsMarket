from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from src.application.interactors.history import ActivityInteractor, HistoryInteractor
from src.domain.entities.history import ActivityDM, HistoryDM


history_router = APIRouter(prefix="/history", tags=["History"])


@history_router.get("")
@inject
async def get_user_history(interactor: FromDishka[HistoryInteractor]) -> list[HistoryDM]:
    """Get user history"""

    return await interactor()


@history_router.get("activity")
@inject
async def get_market_activity(interactor: FromDishka[ActivityInteractor]) -> list[ActivityDM]:
    """Get market market activity"""

    return await interactor()
