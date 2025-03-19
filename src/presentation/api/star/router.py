from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette import status

from src.application.dto.common import ResponseDTO
from src.application.dto.star import CreateStarOrderDTO, StarsIdDTO
from src.application.interactors import star
from src.application.interactors.errors import NotAccessError, NotEnoughBalanceError, NotFoundError
from src.domain.entities.star import StarOrderDM


star_router = APIRouter(prefix="/star", tags=["Stars"])


@star_router.get("/all")
@inject
async def get_all_stars_order(
    interactor: FromDishka[star.GetAllStarOrderInteractor], on_market: bool
) -> list[StarOrderDM]:
    return await interactor(on_market)


@star_router.post("/create")
@inject
async def create_star_order(
    dto: CreateStarOrderDTO, interactor: FromDishka[star.CreateStarOrderInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except (NotEnoughBalanceError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@star_router.post("/buy")
@inject
async def buy_stars(dto: StarsIdDTO, interactor: FromDishka[star.BuyStarsInteractor]) -> ResponseDTO:
    try:
        await interactor(dto)
    except (NotFoundError, NotAccessError, NotEnoughBalanceError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@star_router.post("/cancel")
@inject
async def cancel_stars_order(
    dto: StarsIdDTO, interactor: FromDishka[star.CancelStarOrderInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@star_router.post("/seller-accept")
@inject
async def accept_stars_order(
    dto: StarsIdDTO, interactor: FromDishka[star.SellerAcceptStarOrderInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@star_router.post("/seller-cancel")
@inject
async def seller_accept_stars_order(
    dto: StarsIdDTO, interactor: FromDishka[star.SellerCancelStarOrderInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except (NotFoundError, NotAccessError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@star_router.post("/confirm")
@inject
async def confirm_stars_order(
    dto: StarsIdDTO, interactor: FromDishka[star.ConfirmStarOrderInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@star_router.post("/accept-receipt")
@inject
async def accept_transfer(
    dto: StarsIdDTO, interactor: FromDishka[star.AcceptTransferStarOrderInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@star_router.get("/{id}")
@inject
async def get_star_order_gift(id: int, interactor: FromDishka[star.GetStarOrderInteractor]) -> StarOrderDM:
    try:
        return await interactor(id)
    except (NotFoundError, NotAccessError) as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@star_router.post("/{id}")
@inject
async def edit_star_order(
    id: int, dto: CreateStarOrderDTO, interactor: FromDishka[star.UpdateStarOrderInteractor]
) -> StarOrderDM:
    try:
        return await interactor(id, dto)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@star_router.delete("/{id}")
@inject
async def delete_star_order(id: int, interactor: FromDishka[star.DeleteStarOrderInteractor]) -> ResponseDTO:
    try:
        await interactor(id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)
