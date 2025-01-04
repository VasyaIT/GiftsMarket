from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.transaction import Lt


class TransactionGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_last_lt(self) -> int:
        stmt = select(Lt)
        result = await self._session.execute(stmt)
        return result.scalar_one().last_lt

    async def set_new_lt(self, lt: int) -> None:
        stmt = update(Lt).values(last_lt=lt)
        await self._session.execute(stmt)
