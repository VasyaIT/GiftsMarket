from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.giveaway import GiveawayReader, GiveawaySaver
from src.domain.entities.giveaway import CreateGiveawayDM, GiveawayDM
from src.infrastructure.models.giveaway import Giveaway


class GiveawayGateway(GiveawaySaver, GiveawayReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, data: CreateGiveawayDM) -> GiveawayDM:
        stmt = insert(Giveaway).values(data.model_dump()).returning(Giveaway)
        result = await self._session.execute(stmt)
        return GiveawayDM(**result.scalar_one().__dict__)

    async def get_one(self, **filters) -> GiveawayDM | None:
        stmt = select(Giveaway).filter_by(**filters)
        result = await self._session.execute(stmt)
        if giveaway := result.scalar_one_or_none():
            return GiveawayDM(**giveaway.__dict__)
