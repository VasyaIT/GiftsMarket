from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette import status

from src.application.dto.common import ResponseDTO
from src.application.dto.star import CreateStarOrderDTO
from src.application.interactors import star
from src.application.interactors.errors import NotAccessError, NotFoundError
from src.domain.entities.star import StarOrderDM


start_router = APIRouter(prefix="/star", tags=["Stars"])


@start_router.get("/star/create")
@inject
async def create_star_order(
    dto: CreateStarOrderDTO, interactor: FromDishka[star.CreateStarOrderInteractor]
) -> ResponseDTO:
    await interactor(dto)
    return ResponseDTO(success=True)


@start_router.get("/star/{id}")
@inject
async def get_star_order_gift(id: int, interactor: FromDishka[star.GetStarOrderInteractor]) -> StarOrderDM:
    try:
        return await interactor(id)
    except (NotFoundError, NotAccessError) as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@start_router.post("/star/{id}")
@inject
async def edit_star_order(
    id: int, dto: CreateStarOrderDTO, interactor: FromDishka[star.UpdateStarOrderInteractor]
) -> StarOrderDM:
    try:
        return await interactor(id, dto)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@start_router.delete("/star/{id}")
@inject
async def delete_star_order(id: int, interactor: FromDishka[star.DeleteStarOrderInteractor]) -> ResponseDTO:
    try:
        await interactor(id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)
