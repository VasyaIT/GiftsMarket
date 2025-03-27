from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.history import HistoryReader, HistorySaver
from src.domain.entities.history import ActivityDM, CreateHistoryDM, HistoryDM
from src.infrastructure.models.history import History


class HistoryGateway(HistoryReader, HistorySaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, data: CreateHistoryDM) -> HistoryDM:
        stmt = insert(History).values(data.model_dump()).returning(History)
        result = await self._session.execute(stmt)
        return HistoryDM(**result.scalar_one().__dict__)

    async def save_many(self, data: list[CreateHistoryDM]) -> None:
        stmt = insert(History).values([history.model_dump() for history in data])
        await self._session.execute(stmt)

    async def get_many(self, **filters) -> list[HistoryDM]:
        stmt = select(History).filter_by(**filters)
        result = await self._session.execute(stmt)
        return [HistoryDM(**history.__dict__) for history in result.scalars().all()]

    async def get_activity(self) -> list[ActivityDM]:
        stmt = select(History)
        result = await self._session.execute(stmt)
        return [ActivityDM(**history.__dict__) for history in result.scalars().all()]
