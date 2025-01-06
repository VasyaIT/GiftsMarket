from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.application.dto.common import ResponseDTO
from src.application.dto.market import CreateOrderDTO, OrderIdDTO
from src.application.interactors import market
from src.application.interactors.errors import (
    NotAccessError,
    NotEnoughBalanceError,
    NotFoundError,
    NotUsernameError
)
from src.domain.entities.market import ReadOrderDM
from src.presentation.api.market.params import GiftFilterParams, OrderFilterParams


market_router = APIRouter(prefix="/market", tags=["Market"])


@market_router.get("/gifts")
@inject
async def get_all_gifts(
    filters: Annotated[GiftFilterParams, Depends()], interactor: FromDishka[market.GetGiftsInteractor]
) -> list[ReadOrderDM]:
    return await interactor(filters)


@market_router.get("/order/all")
@inject
async def get_user_orders(
    filters: Annotated[OrderFilterParams, Depends()], interactor: FromDishka[market.GetOrdersInteractor]
) -> list[ReadOrderDM]:
    try:
        return await interactor(filters)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@market_router.post("/order/create")
@inject
async def create_order(
    dto: CreateOrderDTO, interactor: FromDishka[market.CreateOrderInteractor]
) -> ResponseDTO:
    """Create order by user"""

    try:
        await interactor(dto)
    except (NotEnoughBalanceError, NotUsernameError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/order/buy")
@inject
async def buy_gift(dto: OrderIdDTO, interactor: FromDishka[market.BuyGiftInteractor]) -> ResponseDTO:
    """Buyer has paid for the gift and is waiting for the seller transferred the gift"""

    try:
        await interactor(dto.id)
    except (NotFoundError, NotEnoughBalanceError, NotAccessError, NotUsernameError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/order/cancel")
@inject
async def cancel_order(dto: OrderIdDTO, interactor: FromDishka[market.CancelOrderInteractor]) -> ResponseDTO:
    """Buyer can cancel the order until the seller has given him the gift"""

    try:
        await interactor(dto.id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/order/confirm-transfer")
@inject
async def confirm_gift_transfer(
    dto: OrderIdDTO, interactor: FromDishka[market.ConfirmTransferInteractor]
) -> ResponseDTO:
    """When seller transferred gift to buyer, seller confirmed his transfer"""

    try:
        await interactor(dto.id)
    except (NotFoundError, NotAccessError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/order/accept-receipt")
@inject
async def accept_gift_receipt(
    dto: OrderIdDTO, interactor: FromDishka[market.AcceptTransferInteractor]
) -> ResponseDTO:
    """Buyer confirmed receipt of the gift"""

    try:
        await interactor(dto.id)
    except (NotFoundError, NotAccessError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)
