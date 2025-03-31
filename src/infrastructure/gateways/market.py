from datetime import datetime, timezone

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interactors.errors import AlreadyExistError
from src.application.interfaces.market import OrderSaver
from src.domain.entities.cart import CartGiftDM
from src.domain.entities.market import (
    BidDM,
    CreateOrderDM,
    GiftFiltersDM,
    OrderDM,
    ReadOrderDM,
    UserGiftDM,
)
from src.infrastructure.models.order import Bid, Order
from src.presentation.api.market.params import GiftSortParams


class MarketGateway(OrderSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all_gifts(
        self, filters: GiftFiltersDM, sort_by: GiftSortParams | None
    ) -> list[OrderDM]:
        order_by = Order.created_at.desc()
        if sort_by is GiftSortParams.OLDEST:
            order_by = Order.created_at.asc()
        elif sort_by is GiftSortParams.PRICE_LOW_TO_HIGH:
            order_by = Order.price.asc()
        elif sort_by is GiftSortParams.PRICE_HIGH_TO_LOW:
            order_by = Order.price.desc()
        conditions = [
            filters.from_price <= Order.price,
            filters.to_price >= Order.price,
            Order.rarity.in_(filters.rarities),
            Order.is_active == True,
            Order.is_completed == False,
            filters.from_gift_number <= Order.number,
            filters.to_gift_number >= Order.number,
        ]
        if filters.types:
            conditions.append(Order.type.in_(filters.types))
        if filters.model_names:
            conditions.append(Order.model_name.in_(filters.model_names))
        stmt = (
            select(Order)
            .where(*conditions)
            .limit(filters.limit)
            .offset(filters.offset)
            .order_by(Order.is_vip.desc(), order_by)
        )
        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def get_user_gifts(
        self, user_id: int, limit: int | None, offset: int | None
    ) -> list[UserGiftDM]:
        stmt = (
            select(Order)
            .filter_by(seller_id=user_id, is_completed=False)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [UserGiftDM(**order.__dict__) for order in result.scalars().all()]

    async def get_user_gift(self, user_id: int, gift_id: int) -> UserGiftDM | None:
        stmt = select(Order).filter_by(id=gift_id, seller_id=user_id, is_completed=False)
        result = await self._session.execute(stmt)
        if not (gift := result.scalar_one_or_none()):
            return
        return UserGiftDM(**gift.__dict__)

    async def get_many(self, **filters) -> list[OrderDM]:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def get_count_gifts(self) -> int:
        stmt = select(func.count()).select_from(Order)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_one(self, **filters) -> OrderDM | None:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def get_full_order(self, **filters) -> ReadOrderDM | None:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return ReadOrderDM(**order.__dict__)

    async def get_gifts_by_ids(self, gifts_ids: list[int], user_id: int) -> list[CartGiftDM]:
        stmt = select(Order).where(
            Order.id.in_(gifts_ids),
            Order.is_active == True,
            Order.is_completed == False,
            Order.min_step == None,
            Order.seller_id != user_id,
        )
        result = await self._session.execute(stmt)
        return [CartGiftDM(**order.__dict__) for order in result.scalars().all()]

    async def get_auction_orders(self) -> list[OrderDM]:
        stmt = select(Order).where(
            Order.min_step != None,
            Order.auction_end_time <= datetime.now(tz=timezone.utc),
            Order.is_completed == False,
        )
        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def save(self, order_dm: CreateOrderDM) -> CreateOrderDM:
        try:
            stmt = insert(Order).values(order_dm.model_dump()).returning(Order)
        except IntegrityError:
            raise AlreadyExistError("Order already exist")

        result = await self._session.execute(stmt)
        return CreateOrderDM(**result.scalar_one().__dict__)

    async def update_order(self, data: dict, **filters) -> OrderDM | None:
        stmt = update(Order).filter_by(**filters).values(data).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def withdraw_from_market(self, data: dict, **filters) -> UserGiftDM | None:
        stmt = update(Order).filter_by(**filters).values(data).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return UserGiftDM(**order.__dict__)

    async def update_cart_orders(self, values: dict, gifts_ids: list[int], user_id: int) -> None:
        stmt = (
            update(Order)
            .where(
                Order.id.in_(gifts_ids),
                Order.is_active == True,
                Order.is_completed == False,
                Order.min_step == None,
                Order.seller_id != user_id,
            )
            .values(values)
        )
        await self._session.execute(stmt)

    async def delete_order(self, **filters) -> UserGiftDM | None:
        stmt = delete(Order).filter_by(**filters).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return UserGiftDM(**order.__dict__)

    async def save_auction_bid(self, data: BidDM) -> None:
        stmt = insert(Bid).values(data.model_dump())
        await self._session.execute(stmt)

    async def delete_auction_bids(self, **filters) -> None:
        stmt = delete(Bid).filter_by(**filters)
        await self._session.execute(stmt)
