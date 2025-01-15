import logging
from logging.handlers import RotatingFileHandler

from aiogram.utils.payload import decode_payload, encode_payload

from src.application.common.const import OrderStatus, PriceList
from src.application.common.utils import generate_deposit_comment
from src.application.dto.market import OrderDTO, UpdateOrderDTO
from src.application.dto.star import CreateStarOrderDTO
from src.application.dto.user import LoginDTO, UserDTO
from src.application.interactors.errors import NotAccessError, NotFoundError
from src.application.interfaces.auth import InitDataValidator, TokenEncoder
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderReader, OrderSaver
from src.application.interfaces.star import StarOrderReader, StarOrderSaver
from src.application.interfaces.user import UserManager, UserReader, UserSaver
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.market import GetUserGiftsDM, UpdateOrderDM, UserGiftsDM
from src.domain.entities.star import CreateStarOrderDM, StarOrderDM
from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM
from src.entrypoint.config import Config


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    filename="src/logs/star.log",
    maxBytes=1 * 1024 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
logger.addHandler(handler)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


class GetStarOrderInteractor(Interactor[int, StarOrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderReader,
        user_gateway: UserSaver,
        user: UserDM,
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user

    async def __call__(self, order_id: int) -> StarOrderDM:
        order = await self._star_gateway.get_one(id=order_id)
        if not order:
            raise NotFoundError("Star order not found")
        if (
            order.status != OrderStatus.ON_MARKET
            and self._user.id not in (order.seller_id, order.buyer_id)
        ):
            raise NotAccessError("Forbidden")
        return order


class CreateStarOrderInteractor(Interactor[CreateStarOrderDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user

    async def __call__(self, data: CreateStarOrderDTO) -> None:
        await self._star_gateway.save(CreateStarOrderDM(**data.model_dump(), seller_id=self._user.id))

        await self._db_session.commit()


class UpdateStarOrderInteractor:
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user

    async def __call__(self, order_id: int, data: CreateStarOrderDTO) -> StarOrderDM:
        order = await self._star_gateway.update(
            data.model_dump(), id=order_id, seller_id=self._user.id, status=OrderStatus.ON_MARKET
        )
        if not order:
            raise NotFoundError("Star order not found")
        await self._db_session.commit()
        return order


class DeleteStarOrderInteractor(Interactor[int, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user

    async def __call__(self, order_id: int) -> None:
        order = await self._star_gateway.delete(
            id=order_id, seller_id=self._user.id, status=OrderStatus.ON_MARKET
        )
        if not order:
            raise NotFoundError("Star order not found")
        await self._db_session.commit()
