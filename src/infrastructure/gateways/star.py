from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.star import StarOrderSaver
from src.domain.entities.star import CreateStarOrderDM, StarOrderDM
from src.infrastructure.models.star import Star


class StarGateway(StarOrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_one(self, **filters) -> StarOrderDM | None:
        stmt = select(Star).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return StarOrderDM(**order.__dict__)

    async def save(self, star_order: CreateStarOrderDM) -> None:
        stmt = insert(Star).values(star_order.model_dump()).returning(Star)
        await self._session.execute(stmt)

    async def update(self, values: dict, **filters) -> StarOrderDM | None:
        stmt = update(Star).values(values).filter_by(**filters).returning(Star)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return StarOrderDM(**order.__dict__)

    async def delete(self, **filters) -> StarOrderDM | None:
        stmt = delete(Star).filter_by(**filters).returning(Star)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return StarOrderDM(**order.__dict__)
