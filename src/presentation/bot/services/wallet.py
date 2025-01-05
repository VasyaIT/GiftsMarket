from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.wallet import WalletGateway


async def complete_withdraw_request(request_id: int, postgres_config: PostgresConfig) -> None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        await WalletGateway(session).set_completed(request_id)
        await session.commit()
