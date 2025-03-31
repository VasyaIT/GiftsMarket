from src.application.common.const import MAX_WITHDRAW_AMOUNT
from src.application.dto.wallet import WithdrawRequestDTO
from src.application.interactors.errors import NotAccessError, NotEnoughBalanceError
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.user import UserSaver
from src.application.interfaces.wallet import WithdrawRequestSaver
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.domain.entities.wallet import CreateWithdrawRequestDM


class WithdrawRequestInteractor(Interactor[WithdrawRequestDTO, None]):
    def __init__(
        self,
        user_gateway: UserSaver,
        wallet_gateway: WithdrawRequestSaver,
        user: UserDM,
        db_session: DBSession,
    ) -> None:
        self._db_session = db_session
        self._user_gateway = user_gateway
        self._user = user
        self._wallet_gateway = wallet_gateway

    async def __call__(self, data: WithdrawRequestDTO) -> None:
        if self._user.balance < data.amount:
            raise NotEnoughBalanceError("User does not have enough balance")
        if data.amount > MAX_WITHDRAW_AMOUNT:
            raise NotAccessError("Amount is too large")
        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-data.amount)
        )
        await self._wallet_gateway.save(
            CreateWithdrawRequestDM(user_id=self._user.id, amount=data.amount, wallet=data.wallet)
        )
        await self._db_session.commit()
