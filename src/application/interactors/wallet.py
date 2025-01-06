from aiogram import Bot

from src.application.common.utils import send_message
from src.application.dto.wallet import WithdrawRequestDTO
from src.application.interactors.errors import NotEnoughBalanceError
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.user import UserSaver
from src.application.interfaces.wallet import WithdrawRequestSaver
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.domain.entities.wallet import CreateWithdrawRequestDM
from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import withdraw_kb
from src.presentation.bot.services.text import get_withdraw_request_text


class WithdrawRequestInteractor(Interactor[WithdrawRequestDTO, None]):
    def __init__(
        self,
        user_gateway: UserSaver,
        wallet_gateway: WithdrawRequestSaver,
        user: UserDM,
        db_session: DBSession,
        bot: Bot,
        config: Config
    ) -> None:
        self._db_session = db_session
        self._user_gateway = user_gateway
        self._user = user
        self._wallet_gateway = wallet_gateway
        self._bot = bot
        self._config = config

    async def __call__(self, data: WithdrawRequestDTO) -> None:
        if self._user.balance < data.amount:
            raise NotEnoughBalanceError("User does not have enough balance")
        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(
                id=self._user.id,
                amount=-data.amount
            )
        )
        withdraw_request = await self._wallet_gateway.save(
            CreateWithdrawRequestDM(user_id=self._user.id, amount=data.amount, wallet=data.wallet)
        )
        await self._db_session.commit()

        message = get_withdraw_request_text(self._user.username, self._user.id, data.amount, data.wallet)
        await send_message(
            self._bot, message, [self._config.bot.DEPOSIT_CHAT_ID], reply_markup=withdraw_kb(withdraw_request.id)
        )
