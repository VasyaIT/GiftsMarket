from datetime import datetime

from src.application.common.const import GiftType, OrderStatus, PriceList
from src.domain.entities.market import OrderDM, ReadOrderDM
from src.domain.entities.user import UpdateUserBalanceDM
from src.entrypoint.config import Config, PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.gateways.user import UserGateway


async def get_orders_info(
    gift_type: str, gift_number: int, postgres_config: PostgresConfig
) -> list[ReadOrderDM] | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if orders := await MarketGateway(session).get_all(type=GiftType[gift_type], number=gift_number):
            return orders


async def get_gift(order_id: int, postgres_config: PostgresConfig) -> ReadOrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await MarketGateway(session).get_one(id=order_id, status=OrderStatus.ON_MARKET)


async def get_all_inactive(user_id: int, postgres_config: PostgresConfig) -> list[ReadOrderDM]:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await MarketGateway(session).get_all(seller_id=user_id, is_active=False)


async def delete_order(order_id: int, postgres_config: PostgresConfig) -> OrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).delete_order(id=order_id, status=OrderStatus.ON_MARKET):
            return order


async def update_order(data: dict, order_id: int, postgres_config: PostgresConfig) -> OrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).update_order(data, id=order_id):
            await session.commit()
            return order


async def get_count_gifts(postgres_config: PostgresConfig) -> tuple[int, int]:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        gateway = MarketGateway(session)
        count_completed_orders = await gateway.get_count_gifts(is_completed=True)
        count_all_orders = await gateway.get_count_gifts()
    return count_all_orders, count_completed_orders


async def cancel_order(order_id: int, postgres_config: PostgresConfig) -> bool:
    session_maker = new_session_maker(postgres_config)
    data = dict(status=OrderStatus.ON_MARKET, buyer_id=None, created_order_date=None)

    async with session_maker() as session:
        gateway = MarketGateway(session)
        if not (order := await gateway.get_one(id=order_id)):
            return False
        await UserGateway(session).update_balance(
            UpdateUserBalanceDM(
                id=order.buyer_id,
                amount=order.price
            )
        )
        await gateway.update_order(data, id=order_id)
        await session.commit()
    return True


async def confirm_order(order_id: int, config: Config) -> bool:
    session_maker = new_session_maker(config.postgres)
    values = dict(status=OrderStatus.GIFT_RECEIVED, completed_order_date=datetime.now())

    async with session_maker() as session:
        user_gateway = UserGateway(session)
        order = await MarketGateway(session).update_order(
            values, id=order_id, status=OrderStatus.GIFT_TRANSFERRED
        )
        if not order:
            await session.rollback()
            return False

        commission = order.price * PriceList.SELLER_FEE_PERCENT / 100
        if order.seller_id in config.bot.nft_holders_id:
            commission = 0
        await user_gateway.update_balance(
            UpdateUserBalanceDM(id=order.seller_id, amount=order.price - commission)
        )
        referrer = await user_gateway.get_referrer(user_id=order.seller_id)
        if referrer:
            referrer_percent = PriceList.REFERRAL_PERCENT
            if referrer.id in config.app.vip_users_id:
                referrer_percent = PriceList.VIP_REFERRAL_PERCENT
            referrer_reward = commission * referrer_percent / 100
            await user_gateway.update_referrer_balance(referrer.id, referrer_reward)

        await session.commit()
    return True
