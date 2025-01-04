from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.market import OrderSaver
from src.domain.entities.market import CreateOrderDM, OrderDM, UpdateOrderStatusDM
from src.infrastructure.models.order import Order


class MarketGateway(OrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self, offset: int = 0, limit: int | None = None) -> list[OrderDM]:
        stmt = select(Order).filter_by().limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def get_by_id(self, order_id: int) -> OrderDM | None:
        stmt = select(Order).filter_by(id=order_id)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def save(self, order_dm: CreateOrderDM) -> None:
        stmt = insert(Order).values(order_dm.model_dump())
        await self._session.execute(stmt)

    async def update_status(self, data: UpdateOrderStatusDM) -> OrderDM | None:
        values: dict = {"status": data.new_status}
        if data.buyer_id:
            values["buyer_id"] = data.buyer_id
        stmt = update(Order).filter_by(id=data.id, status=data.old_status).values(values)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)
