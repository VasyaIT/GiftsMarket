from src.domain.entities.market import OrderDM
from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway


async def activate_order(order_id: int, postgres_config: PostgresConfig) -> OrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).update_order(dict(is_active=True), id=order_id):
            await session.commit()
            return order
