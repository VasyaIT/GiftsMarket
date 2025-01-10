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


async def ban_user(postgres_config: PostgresConfig, user_id: int) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if await UserGateway(session).update_user(dict(is_banned=True), id=user_id):
            await session.commit()
            return True
    return False


async def unban_user(postgres_config: PostgresConfig, user_id: int) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if await UserGateway(session).update_user(dict(is_banned=False), id=user_id):
            await session.commit()
            return True
    return False
