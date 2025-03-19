from tonutils.client import TonapiClient
from tonutils.wallet import WalletV5R1

from src.application.common.const import HistoryType
from src.domain.entities.history import CreateHistoryDM
from src.domain.entities.wallet import WithdrawRequestDM
from src.entrypoint.config import PostgresConfig, TonapiConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.history import HistoryGateway
from src.infrastructure.gateways.wallet import WalletGateway


async def get_withdraw_request(
    request_id: int, postgres_config: PostgresConfig
) -> WithdrawRequestDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if withdraw_request := await WalletGateway(session).get_one(id=request_id, is_completed=False):
            return withdraw_request


async def complete_withdraw_request(
    request_id: int, postgres_config: PostgresConfig
) -> WithdrawRequestDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if withdraw_request := await WalletGateway(session).set_completed(request_id):
            history_data = CreateHistoryDM(
                user_id=withdraw_request.user_id,
                price=withdraw_request.amount,
                type=HistoryType.WITHDRAW
            )
            await HistoryGateway(session).save(history_data)
            await session.commit()
            return withdraw_request


async def send_transaction(
    withdraw_request: WithdrawRequestDM, ton_config: TonapiConfig
) -> WithdrawRequestDM | None:
    client = TonapiClient(api_key=ton_config.TONAPI_TOKEN, is_testnet=ton_config.IS_TESTNET)
    wallet, _, _, _ = WalletV5R1.from_mnemonic(client, ton_config.WALLET_MNEMONICS)
    await wallet.transfer(withdraw_request.wallet, withdraw_request.amount)
