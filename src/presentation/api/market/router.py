from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.application.dto.common import GiftImagesDTO, ResponseDTO
from src.application.dto.market import CreateOrderDTO, OrderIdDTO
from src.application.interactors import errors, market
from src.domain.entities.market import OrderDM
from src.presentation.api.market.params import GiftFilterParams, GiftSortParams


market_router = APIRouter(prefix="/market", tags=["Market"])


@market_router.get("/gifts")
@inject
async def get_all_gifts(
    filters: Annotated[GiftFilterParams, Depends()],
    interactor: FromDishka[market.GetGiftsInteractor],
    sort_by: GiftSortParams | None = None,
) -> list[OrderDM]:
    return await interactor(filters, sort_by)


@market_router.get("/gifts/{id}")
@inject
async def get_gift_by_id(id: int, interactor: FromDishka[market.GetGiftInteractor]) -> OrderDM:
    try:
        return await interactor(id)
    except errors.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@market_router.post("/order/create")
@inject
async def create_order(
    dto: CreateOrderDTO, interactor: FromDishka[market.CreateOrderInteractor]
) -> ResponseDTO:
    """Create order by user"""

    try:
        await interactor(dto)
    except (errors.NotEnoughBalanceError, errors.NotAccessError, errors.AlreadyExistError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/order/buy")
@inject
async def buy_gift(dto: OrderIdDTO, interactor: FromDishka[market.BuyGiftInteractor]) -> ResponseDTO:
    """Buyer has paid for the gift and is waiting for the seller transferred the gift"""

    try:
        await interactor(dto.id)
    except (
        errors.NotFoundError, errors.NotEnoughBalanceError, errors.NotAccessError, errors.GiftSendError
    ) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.get("/get-gift-types")
@inject
async def get_images_by_gift_type(image_data: FromDishka[GiftImagesDTO]) -> GiftImagesDTO:
    return image_data
