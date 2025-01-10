from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.gateways.user import UserGateway


async def get_count_users(postgres_config: PostgresConfig) -> int:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await UserGateway(session).get_count_users()


async def get_count_gifts(postgres_config: PostgresConfig) -> int:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await MarketGateway(session).get_count_gifts()
