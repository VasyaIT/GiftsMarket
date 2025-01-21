from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.application.dto.common import ResponseDTO
from src.application.dto.sticker import BidDTO, CreateAuctionDTO
from src.application.interactors import sticker
from src.application.interactors.errors import NotFoundError
from src.domain.entities.sticker import AuctionDM


sticker_router = APIRouter(prefix="/auction", tags=["Auction"])


@sticker_router.post("/create")
@inject
async def create_auction(
    dto: CreateAuctionDTO, interactor: FromDishka[sticker.CreateAuctionInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except NotFoundError as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@sticker_router.post("/bid")
@inject
async def new_bid(dto: BidDTO, interactor: FromDishka[sticker.NewBidInteractor]) -> ResponseDTO:
    try:
        await interactor(dto)
    except NotFoundError as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@sticker_router.get("/all")
@inject
async def get_all_auctions(interactor: FromDishka[sticker.GetAllAuctionsInteractor]) -> list[AuctionDM]:
    return await interactor()


@sticker_router.get("/{id}")
@inject
async def get_auction_by_id(id: int, interactor: FromDishka[sticker.GetAuctionInteractor]) -> AuctionDM:
    try:
        return await interactor(id)
    except NotFoundError as e:
        raise HTTPException(HTTP_404_NOT_FOUND, str(e))
