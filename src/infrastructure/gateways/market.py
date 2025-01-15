from sqlalchemy import and_, delete, func, insert, or_, select, update
from sqlalchemy.exc import DBAPIError
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
from src.infrastructure.gateways.errors import InvalidOrderDataError
from src.infrastructure.models.order import Order
from src.presentation.api.market.params import GiftSortParams


class MarketGateway(OrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all_gifts(self, filters: GiftFiltersDM, sort_by: GiftSortParams | None) -> list[ReadOrderDM]:
        order_by = Order.created_at.desc()
        if sort_by is GiftSortParams.OLDEST:
            order_by = Order.created_at.asc()
        elif sort_by is GiftSortParams.PRICE_LOW_TO_HIGH:
            order_by = Order.price.asc()
        elif sort_by is GiftSortParams.PRICE_HIGH_TO_LOW:
            order_by = Order.price.desc()
        stmt = (
            select(Order)
            .where(
                filters.from_price <= Order.price, filters.to_price >= Order.price,
                Order.rarity.in_(filters.rarities), Order.type.in_(filters.types),
                Order.status == filters.status, Order.is_active == True,
            )
            .limit(filters.limit)
            .offset(filters.offset)
            .order_by(Order.is_vip.desc(), order_by)
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
            .order_by(Order.created_at.desc())
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
        stmt = (
            select(Order)
            .filter_by(seller_id=data.user_id, status=data.status)
            .order_by(Order.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [UserGiftsDM(**order.__dict__) for order in result.scalars().all()]

    async def get_all(self, **filters) -> list[ReadOrderDM]:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        return [
            ReadOrderDM(
                **order.__dict__,
                seller_name=order.seller.username,
                buyer_name=None if not order.buyer else order.buyer.username,
            ) for order in result.scalars().all()
        ]

    async def get_user_orders(self, user_id: int) -> list[OrderDM]:
        stmt = (
            select(Order).where(
                and_(
                    Order.status.in_(
                        [OrderStatus.SELLER_ACCEPT, OrderStatus.GIFT_TRANSFERRED, OrderStatus.GIFT_RECEIVED]
                    ),
                    or_(Order.seller_id == user_id, Order.buyer_id == user_id)
                )
            )
        )
        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def get_count_gifts(self, is_completed: bool = False) -> int:
        filters = dict(status=OrderStatus.GIFT_RECEIVED) if is_completed else dict()
        stmt = select(func.count()).select_from(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_one(self, **filters) -> ReadOrderDM | None:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return ReadOrderDM(
                **order.__dict__,
                seller_name=order.seller.username,
                buyer_name=None if not order.buyer else order.buyer.username
            )

    async def is_exist(self, **filters) -> bool:
        stmt = select(Order).filter_by(**filters).where(Order.status != OrderStatus.GIFT_RECEIVED)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

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
                        and_(
                            Order.status == OrderStatus.SELLER_ACCEPT,
                            or_(Order.buyer_id == user_id, Order.seller_id == user_id)
                        ),
                    )
                )
            )
        )
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def save(self, order_dm: CreateOrderDM) -> OrderDM:
        try:
            stmt = insert(Order).values(order_dm.model_dump()).returning(Order)
        except DBAPIError:
            raise InvalidOrderDataError("Order already exist")

        result = await self._session.execute(stmt)
        return OrderDM(**result.scalar_one().__dict__)

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
