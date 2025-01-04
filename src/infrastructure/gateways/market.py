from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.auth import TokenDecoder, TokenEncoder
from src.application.interfaces.market import OrderSaver
from src.domain.entities.market import CreateOrderDM, OrderDM
from src.infrastructure.models.order import Order


class MarketGateway(OrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self, offset: int = 0, limit: int | None = None) -> list[OrderDM]:
        stmt = select(Order).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def save(self, order_dm: CreateOrderDM) -> None:
        stmt = insert(Order).values(order_dm.model_dump())
        await self._session.execute(stmt)
