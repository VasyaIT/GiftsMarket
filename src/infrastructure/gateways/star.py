from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.const import OrderStatus
from src.application.interfaces.star import StarOrderSaver
from src.domain.entities.star import CreateStarOrderDM, StarOrderDM
from src.infrastructure.models.star import Star


class StarGateway(StarOrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self, **filters) -> list[StarOrderDM]:
        stmt = select(Star).filter_by(**filters)
        result = await self._session.execute(stmt)
        return [StarOrderDM(**order.__dict__) for order in result.scalars().all()]

    async def get_all_orders(self, **filters) -> list[StarOrderDM]:
        stmt = select(Star).filter_by(**filters)
        result = await self._session.execute(stmt)
        return [StarOrderDM(**order.__dict__) for order in result.scalars().all()]

    async def get_one(self, **filters) -> StarOrderDM | None:
        stmt = select(Star).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return StarOrderDM(**order.__dict__)

    async def get_cancel_order(self, order_id: int, user_id: int) -> StarOrderDM | None:
        stmt = (
            select(Star)
            .where(
                and_(
                    Star.id == order_id,
                    or_(
                        and_(Star.status == OrderStatus.BUY, Star.seller_id == user_id),
                        and_(
                            Star.status == OrderStatus.SELLER_ACCEPT,
                            or_(Star.buyer_id == user_id, Star.seller_id == user_id)
                        ),
                    )
                )
            )
        )
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
