from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.star import StarOrderSaver
from src.domain.entities.sticker import AuctionDM, NewBidDM, StickerOrderDM
from src.infrastructure.models.sticker import Auction


class StickerGateway(StarOrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self, **filters) -> list[AuctionDM]:
        stmt = select(Auction).filter_by(**filters)
        result = await self._session.execute(stmt)
        return [AuctionDM(**order.__dict__) for order in result.scalars().all()]

    async def get_one(self, **filters) -> AuctionDM | None:
        stmt = select(Auction).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return AuctionDM(**order.__dict__)

    async def new_bid(self, data: NewBidDM) -> StickerOrderDM | None:
        stmt = (
            update(Auction)
            .where(Auction.id == data.id, Auction.last_bid < data.amount)
            .values(buyer_id=data.buyer_id, last_bid=data.amount)
            .returning(Auction)
        )
        result = await self._session.execute(stmt)
        auction = result.scalar_one_or_none()
        if auction:
            return StickerOrderDM(**auction.__dict__)
