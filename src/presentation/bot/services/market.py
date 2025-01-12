from src.application.common.const import OrderStatus, PriceList
from src.domain.entities.market import OrderDM
from src.domain.entities.user import UpdateUserBalanceDM
from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.gateways.user import UserGateway


async def get_all_inactive(user_id: int, postgres_config: PostgresConfig) -> list[OrderDM]:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await MarketGateway(session).get_all(seller_id=user_id, is_active=False)


async def delete_order(order_id: int, postgres_config: PostgresConfig) -> OrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).delete_order(id=order_id):
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
                amount=order.price + PriceList.BUYER_FEE_TON
            )
        )
        await gateway.update_order(data, id=order_id)
    return True
