from src.domain.entities.market import OrderDM, ReadOrderDM
from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway


async def get_one(order_id: int, postgres_config: PostgresConfig) -> ReadOrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).get_one(id=order_id):
            return order


async def activate_order(order_id: int, postgres_config: PostgresConfig) -> OrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).update_order(dict(is_active=True), id=order_id):
            await session.commit()
            return order


async def get_count_gifts(postgres_config: PostgresConfig) -> tuple[int, int]:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        gateway = MarketGateway(session)
        count_completed_orders = await gateway.get_count_gifts(is_completed=True)
        count_all_orders = await gateway.get_count_gifts()
    return count_all_orders, count_completed_orders
