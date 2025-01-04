from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status

from src.application.dto.common import ResponseDTO
from src.application.dto.market import CreateOrderDTO, OrderIdDTO
from src.application.interactors.errors import NotAccessError, NotEnoughBalanceError, NotFoundError
from src.application.interactors.market import (
    AcceptTransferInteractor,
    BuyGiftInteractor,
    ConfirmTransferInteractor,
    CreateOrderInteractor,
    GetOrderInteractor,
    GetOrdersInteractor
)
from src.domain.entities.market import OrderDM
from src.presentation.api.params import FilterParams


market_router = APIRouter(prefix="/orders", tags=["Market"])


@market_router.get("/{id}")
@inject
async def get_order_by_id(id: int, interactor: FromDishka[GetOrderInteractor]) -> OrderDM:
    try:
        return await interactor(id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@market_router.get("/all")
@inject
async def get_all_orders(
    filters: Annotated[FilterParams, Depends()], interactor: FromDishka[GetOrdersInteractor]
) -> list[OrderDM]:
    return await interactor(filters)


@market_router.post("/create")
@inject
async def create_order(
    dto: CreateOrderDTO, interactor: FromDishka[CreateOrderInteractor]
) -> ResponseDTO:
    """Create order by user"""

    try:
        await interactor(dto)
    except NotEnoughBalanceError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/buy")
@inject
async def buy_gift(dto: OrderIdDTO, interactor: FromDishka[BuyGiftInteractor]) -> ResponseDTO:
    """Buyer has paid for the gift and is waiting for the seller transferred the gift"""

    try:
        await interactor(dto.id)
    except (NotFoundError, NotEnoughBalanceError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/confirm-transfer")
@inject
async def confirm_gift_transfer(
    dto: OrderIdDTO, interactor: FromDishka[ConfirmTransferInteractor]
) -> ResponseDTO:
    """When seller transferred gift to buyer, seller confirmed his transfer"""

    try:
        await interactor(dto.id)
    except (NotFoundError, NotAccessError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/accept-receipt")
@inject
async def accept_gift_receipt(
    dto: OrderIdDTO, interactor: FromDishka[AcceptTransferInteractor]
) -> ResponseDTO:
    """Buyer confirmed receipt of the gift"""

    try:
        await interactor(dto.id)
    except (NotFoundError, NotAccessError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)
