from aiogram import Bot
from tonutils.client import TonapiClient
from tonutils.wallet import WalletV5R1

from src.application.common.const import HistoryType
from src.application.common.utils import send_message
from src.domain.entities.history import CreateHistoryDM
from src.domain.entities.wallet import WithdrawRequestDM
from src.entrypoint.config import Config, PostgresConfig, TonapiConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.history import HistoryGateway
from src.infrastructure.gateways.wallet import WalletGateway


async def run_tracker(config: Config, bot: Bot) -> None:
    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        requests = await WalletGateway(session).get_many(is_completed=False)
    for request in requests:
        await send_transaction(request, config.tonapi)
        await complete_withdraw_request(request.id, config.postgres)
        await send_message(bot, f"✅ Вывод {request.amount:.2f} TON исполнен", [request.user_id])
        await send_message(
            bot,
            f"👛 Пользователь #{request.user_id} вывел {request.amount:.2f} TON",
            [config.bot.DEPOSIT_CHAT_ID],
            message_thread_id=config.bot.MODERATION_THREAD_ID,
        )


async def complete_withdraw_request(
    request_id: int, postgres_config: PostgresConfig
) -> WithdrawRequestDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if withdraw_request := await WalletGateway(session).set_completed(request_id):
            history_data = CreateHistoryDM(
                user_id=withdraw_request.user_id,
                price=withdraw_request.amount,
                type=HistoryType.WITHDRAW,
            )
            await HistoryGateway(session).save(history_data)
            await session.commit()
            return withdraw_request


async def send_transaction(withdraw_request: WithdrawRequestDM, ton_config: TonapiConfig) -> None:
    client = TonapiClient(api_key=ton_config.TONAPI_TOKEN, is_testnet=ton_config.IS_TESTNET)
    wallet, _, _, _ = WalletV5R1.from_mnemonic(client, ton_config.WALLET_MNEMONICS)
    await wallet.transfer(withdraw_request.wallet, withdraw_request.amount)
