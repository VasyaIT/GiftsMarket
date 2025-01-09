from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.const import OrderStatus
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
                Order.status == filters.status, Order.seller_id != filters.user_id,
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
        user_filters = dict()
        if filters.is_buyer:
            user_filters["buyer_id"] = filters.user_id
        elif filters.is_seller:
            user_filters["seller_id"] = filters.user_id

        stmt = (
            select(Order)
            .where(
                Order.status.in_(filters.statuses),
                or_(Order.buyer_id == filters.user_id, Order.seller_id == filters.user_id)
            )
            .filter_by(**user_filters)
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
                    buyer_name=order.buyer.username,
                )
            )
        return order_rm

    async def get_user_gifts(self, data: GetUserGiftsDM) -> list[UserGiftsDM]:
        stmt = select(Order).filter_by(seller_id=data.user_id, status=data.status)
        result = await self._session.execute(stmt)
        return [UserGiftsDM(**order.__dict__) for order in result.scalars().all()]

    async def get_by_id(self, **filters) -> ReadOrderDM | None:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return ReadOrderDM(
                **order.__dict__,
                seller_name=order.seller.username,
                buyer_name=None if not order.buyer else order.buyer.username
            )

    async def get_by_id_and_user(
        self, order_id: int, user_id: int, statuses: list[OrderStatus]
    ) -> ReadOrderDM | None:
        stmt = (
            select(Order)
            .where(
                Order.id == order_id,
                Order.status.in_(statuses),
                or_(Order.buyer_id == user_id, Order.seller_id == user_id)
            )
        )
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return ReadOrderDM(
                **order.__dict__,
                seller_name=order.seller.username,
                buyer_name=order.buyer.username
            )

    async def get_cancel_order(self, order_id: int, user_id: int) -> OrderDM | None:
        stmt = (
            select(Order)
            .where(
                and_(
                    Order.id == order_id,
                    or_(
                        and_(Order.status == OrderStatus.BUY, Order.seller_id == user_id),
                        and_(Order.status == OrderStatus.SELLER_ACCEPT, Order.buyer_id == user_id),
                    )
                )
            )
        )
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

    async def seller_cancel_order(self, order_id: int, user_id: int, data: dict) -> OrderDM | None:
        stmt = (
            update(Order)
            .where(
                and_(
                    Order.id == order_id,
                    or_(
                        and_(Order.status == OrderStatus.BUY, Order.seller_id == user_id),
                        and_(Order.status == OrderStatus.SELLER_ACCEPT, Order.buyer_id == user_id),
                    )
                )
            )
            .values(data)
            .returning(Order)
        )
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
