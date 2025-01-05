from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.market import OrderSaver
from src.domain.entities.market import (
    CreateOrderDM,
    GiftFiltersDM,
    OrderDM,
    OrderFiltersDM,
    ReadOrderDM,
    UpdateOrderStatusDM
)
from src.infrastructure.models.order import Order


class MarketGateway(OrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all_gifts(self, filters: GiftFiltersDM) -> list[ReadOrderDM]:
        stmt = (
            select(Order)
            .where(
                filters.from_price < Order.price, filters.to_price > Order.price,
                Order.rarity.in_(filters.rarities), Order.type.in_(filters.types),
                Order.status == filters.status
            )
            .limit(filters.limit)
            .offset(filters.offset)
        )
        result = await self._session.execute(stmt)
        order_rm = []
        for order in result.scalars().all():
            order_rm.append(
                ReadOrderDM(
                    **order.__dict__,
                    seller_name=order.seller.first_name,
                    buyer_name=order.buyer.first_name
                )
            )
        return order_rm

    async def get_all_orders(self, filters: OrderFiltersDM) -> list[ReadOrderDM]:
        stmt = (
            select(Order)
            .where(
                Order.status.in_(filters.statuses)
            )
            .limit(filters.limit)
            .offset(filters.offset)
        )
        result = await self._session.execute(stmt)
        order_rm = []
        for order in result.scalars().all():
            order_rm.append(
                ReadOrderDM(
                    **order.__dict__,
                    seller_name=order.seller.first_name,
                    buyer_name=order.buyer.first_name
                )
            )
        return order_rm

    async def get_by_id(self, order_id: int) -> OrderDM | None:
        stmt = select(Order).filter_by(id=order_id)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def save(self, order_dm: CreateOrderDM) -> None:
        stmt = insert(Order).values(order_dm.model_dump())
        await self._session.execute(stmt)

    async def update_status(self, data: UpdateOrderStatusDM, consider_buyers: bool = False) -> OrderDM | None:
        values: dict = {"status": data.new_status}
        filters = {"id": data.id, "status": data.current_status}
        if consider_buyers:
            values["buyer_id"] = data.new_buyer_id
            filters["buyer_id"] = data.current_buyer_id
        stmt = (update(Order).filter_by(**filters).values(values).returning(Order))
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)
