from src.application.common.const import PriceList
from src.application.dto.sticker import BidDTO, CreateAuctionDTO
from src.application.interactors import errors
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.sticker import AuctionReader, AuctionSaver
from src.application.interfaces.user import UserSaver
from src.domain.entities.sticker import AuctionDM, NewBidDM
from src.domain.entities.user import UpdateUserBalanceDM, UserDM


class CreateAuctionInteractor(Interactor[CreateAuctionDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        sticker_gateway: AuctionSaver,
        user_gateway: UserSaver,
        user: UserDM,
    ) -> None:
        self._db_session = db_session
        self._sticker_gateway = sticker_gateway
        self._user_gateway = user_gateway
        self._user = user

    async def __call__(self, data: CreateAuctionDTO) -> None:
        updated_user = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-PriceList.CREATE_AUCTION)
        )
        if not updated_user or updated_user.balance < 0:
            await self._db_session.rollback()
            raise errors.NotEnoughBalanceError("User does not have enough balance")
        await self._sticker_gateway.save(data.model_dump())
        await self._db_session.commit()


class NewBidInteractor(Interactor[BidDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        sticker_gateway: AuctionSaver,
        user: UserDM,
    ) -> None:
        self._db_session = db_session
        self._sticker_gateway = sticker_gateway
        self._user = user

    async def __call__(self, data: BidDTO) -> None:
        auction = await self._sticker_gateway.new_bid(
            NewBidDM(id=data.id, amount=data.amount, buyer_id=self._user.id)
        )
        if not auction:
            await self._db_session.rollback()
            raise errors.NotFoundError("Auction not found or the bid amount is low")
        await self._db_session.commit()


class GetAllAuctionsInteractor(Interactor[None, list[AuctionDM]]):
    def __init__(self, sticker_gateway: AuctionReader) -> None:
        self._sticker_gateway = sticker_gateway

    async def __call__(self) -> list[AuctionDM]:
        return await self._sticker_gateway.get_all()


class GetAuctionInteractor(Interactor[id: int, AuctionDM]):
    def __init__(self, sticker_gateway: AuctionReader) -> None:
        self._sticker_gateway = sticker_gateway

    async def __call__(self, id: int) -> AuctionDM:
        auction = await self._sticker_gateway.get_one(id=id)
        if not auction:
            raise errors.NotFoundError("Auction not found")
        return auction
