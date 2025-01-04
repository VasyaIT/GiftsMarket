from src.application.common.const import PriceList
from src.application.dto.market import CreateOrderDTO
from src.application.dto.user import LoginDTO
from src.application.interactors.errors import NotEnoughBalanceError
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderReader, OrderSaver
from src.application.interfaces.user import UserReader, UserSaver
from src.domain.entities.market import CreateOrderDM, OrderDM
from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM
from src.presentation.api.params import FilterParams


class CreateOrderInteractor(Interactor[CreateOrderDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderSaver,
        user: UserDM,
        user_gateway: UserSaver,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user = user
        self._user_gateway = user_gateway

    async def __call__(self, data: CreateOrderDTO) -> None:
        await self._market_gateway.save(
            CreateOrderDM(image_url="", title=data.title, amount=data.amount, seller_id=self._user.id)
        )
        updated_user = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-PriceList.UP_FOR_SALE)
        )
        if not updated_user or updated_user.balance < 0:
            await self._db_session.rollback()
            raise NotEnoughBalanceError("User does not have enough balance")
        await self._db_session.commit()


class GetOrdersInteractor(Interactor[FilterParams, list[OrderDM]]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderReader,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway

    async def __call__(self, data: FilterParams) -> list[OrderDM]:
        return await self._market_gateway.get_all(data.offset, data.limit)
