from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.application.dto.giveaway import CreateGiveawayDTO
from src.application.interactors import errors
from src.application.interactors import giveaway as interactors
from src.domain.entities.giveaway import GiveawayDM, TelegramChannelDM


giveaway_router = APIRouter(tags=["Giveaway"])


@giveaway_router.post("/giveaway/create")
@inject
async def create_giveaway(
    dto: CreateGiveawayDTO, interactor: FromDishka[interactors.CreateGiveawayInteractor]
) -> None:
    return await interactor(dto)


@giveaway_router.post("/giveaway/{id}/join")
@inject
async def check_giveaway_subscribes(
    id: int, interactor: FromDishka[interactors.GiveawayJoinInteractor]
) -> None:
    try:
        return await interactor(id)
    except (errors.NotFoundError, errors.GiveawaySubscriptionError, errors.NotEnoughBalanceError) as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, str(e))


@giveaway_router.post("/giveaway/{id}")
@inject
async def get_giveaway(id: int, interactor: FromDishka[interactors.GetGiveawayInteractor]) -> GiveawayDM:
    try:
        return await interactor(id)
    except errors.NotFoundError as e:
        raise HTTPException(HTTP_404_NOT_FOUND, str(e))


@giveaway_router.get("/telegram/channel/{username}")
@inject
async def get_telegram_channel_info(
    username: str, interactor: FromDishka[interactors.TelegramChannelInfoInteractor]
) -> TelegramChannelDM:
    """Get telegram channel info by username"""

    try:
        return await interactor(username)
    except errors.NotFoundError as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, str(e))
