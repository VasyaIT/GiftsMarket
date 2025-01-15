from src.domain.entities.user import FullUserInfoDM, UpdateUserBalanceDM
from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.gateways.user import UserGateway
from src.infrastructure.gateways.wallet import WalletGateway


async def get_count_users(postgres_config: PostgresConfig) -> int:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await UserGateway(session).get_count_users()


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


async def add_balance_user(postgres_config: PostgresConfig, user_id: int, amount: float) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if await UserGateway(session).update_balance(UpdateUserBalanceDM(id=user_id, amount=amount)):
            await session.commit()
            return True
    return False


async def get_full_user_info(postgres_config: PostgresConfig, user_id: int) -> FullUserInfoDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        gateway = UserGateway(session)
        if not (user := await gateway.get_by_id(user_id)):
            return
        orders = await MarketGateway(session).get_user_orders(user_id)
        withdraw_requests, total_withdrawn = await WalletGateway(session).get_by_user_id(user_id)

    return FullUserInfoDM(
        **user.model_dump(),
        orders=orders,
        withdraw_requests=withdraw_requests,
        total_withdrawn=total_withdrawn,
    )


async def get_total_balance(postgres_config: PostgresConfig) -> float:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await UserGateway(session).get_sum_users_balance()
