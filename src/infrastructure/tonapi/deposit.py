from aiogram import Bot
from pytonapi import AsyncTonapi

from src.application.common.utils import send_message
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.entrypoint.config import Config, PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.transaction import TransactionGateway
from src.infrastructure.gateways.user import UserGateway


async def run_tracker(config: Config, bot: Bot) -> None:
    tonapi = AsyncTonapi(config.tonapi.TONAPI_TOKEN, is_testnet=config.tonapi.IS_TESTNET)
    after_lt = await get_last_lt(config.postgres)
    try:
        result = await tonapi.blockchain.get_account_transactions(
            account_id=config.tonapi.DEPOSIT_ADDRESS, after_lt=after_lt, limit=30
        )
    except Exception:
        return
    if not (transactions := result.transactions[::-1]):
        return
    for transaction in transactions:
        if not transaction.success:
            continue
        in_msg = transaction.in_msg

        if not (
            in_msg and in_msg.destination and in_msg.source
            and in_msg.destination.address.to_userfriendly() == config.tonapi.DEPOSIT_ADDRESS
        ):
            continue

        ton_amount = in_msg.value / 1e9
        try:
            comment = in_msg.decoded_body["text"]  # type: ignore
        except (KeyError, TypeError):
            continue
        if ton_amount <= 0:
            continue
        user = await update_user_balance_and_lt(comment, ton_amount, transaction.lt, config.postgres)
        if user:
            user_data_text = f"{f'@{user.username}' if user.username else ''} #<code>{user.id}</code>"
            link_text = "testnet." if config.tonapi.IS_TESTNET else ""
            await send_message(
                bot,
                f"💸 {user_data_text.strip()} пополнил баланс на {ton_amount} TON\n\n"
                f"🔗 <b><a href='https://{link_text}tonviewer.com/transaction/{transaction.hash}'>Транзакция</a></b>",
                [config.bot.DEPOSIT_CHAT_ID]
            )
            await bot.session.close()


async def update_user_balance_and_lt(
        comment: str, ton_amount: float, new_lt: int, postgres_config: PostgresConfig
) -> UserDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        user = await UserGateway(session).update_balance(
            UpdateUserBalanceDM(amount=ton_amount, deposit_comment=comment)
        )
        if not user:
            return
        await TransactionGateway(session).set_new_lt(new_lt)
        await session.commit()
        return user


async def get_last_lt(postgres_config: PostgresConfig) -> int:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await TransactionGateway(session).get_last_lt()
