from sqlalchemy import ColumnExpressionArgument, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.market import OrderSaver
from src.domain.entities.market import (
    CreateOrderDM,
    GetUserGiftsDM,
    GiftFiltersDM,
    OrderDM,
    OrderFiltersDM,
    ReadOrderDM,
    UserGiftsDM
)
from src.infrastructure.models.order import Order


class MarketGateway(OrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all_gifts(self, filters: GiftFiltersDM) -> list[ReadOrderDM]:
        stmt = (
            select(Order)
            .where(
                filters.from_price <= Order.price, filters.to_price >= Order.price,
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
                    seller_name=order.seller.username,
                    buyer_name=None if not order.buyer else order.buyer.username
                )
            )
        return order_rm

    async def get_all_orders(self, filters: OrderFiltersDM) -> list[ReadOrderDM]:
        conditions: list[ColumnExpressionArgument[bool]] = [Order.status.in_(filters.statuses)]
        if filters.buyer_id:
            conditions.append(Order.buyer_id == filters.buyer_id)
        elif filters.seller_id:
            conditions.append(Order.seller_id == filters.seller_id)

        stmt = select(Order).where(*conditions).limit(filters.limit).offset(filters.offset)
        result = await self._session.execute(stmt)
        order_rm = []
        for order in result.scalars().all():
            order_rm.append(
                ReadOrderDM(
                    **order.__dict__,
                    seller_name=order.seller.username,
                    buyer_name=order.buyer.username,
                )
            )
        return order_rm

    async def get_user_gifts(self, data: GetUserGiftsDM) -> list[UserGiftsDM]:
        stmt = select(Order).filter_by(seller_id=data.user_id, status=data.status)
        result = await self._session.execute(stmt)
        return [UserGiftsDM(**order.__dict__) for order in result.scalars().all()]

    async def get_by_id(self, order_id: int) -> OrderDM | None:
        stmt = select(Order).filter_by(id=order_id)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def save(self, order_dm: CreateOrderDM) -> None:
        stmt = insert(Order).values(order_dm.model_dump())
        await self._session.execute(stmt)

    async def update_order(self, data: dict, **filters) -> OrderDM | None:
        stmt = update(Order).filter_by(**filters).values(data).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def delete_order(self, **filters) -> OrderDM | None:
        stmt = delete(Order).filter_by(**filters).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)
