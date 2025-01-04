from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status

from src.application.dto.market import CreateOrderDTO
from src.application.interactors.errors import NotEnoughBalanceError
from src.application.interactors.market import CreateOrderInteractor, GetOrdersInteractor
from src.domain.entities.market import OrderDM
from src.presentation.api.params import FilterParams


market_router = APIRouter(prefix="/orders", tags=["Market"])


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
) -> dict[str, bool]:
    try:
        await interactor(dto)
    except NotEnoughBalanceError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return {"success": True}
