import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot
from aiogram.utils.payload import decode_payload, encode_payload
from pyrogram.client import Client

from src.application.common.send_gift import send_gift
from src.application.common.utils import build_direct_link, generate_deposit_comment
from src.application.dto.market import UpdateOrderDTO
from src.application.dto.user import LoginDTO, UserDTO
from src.application.interactors.errors import GiftSendError, NotFoundError
from src.application.interfaces.auth import InitDataValidator, TokenEncoder
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderReader, OrderSaver
from src.application.interfaces.user import UserManager, UserReader, UserSaver
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.market import OrderDM, UserGiftDM
from src.domain.entities.user import CreateUserDM, UserDM
from src.entrypoint.config import Config


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    filename="src/logs/user.log",
    maxBytes=1 * 1024 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
logger.addHandler(handler)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


class LoginInteractor(Interactor[LoginDTO, str]):
    def __init__(
        self,
        db_session: DBSession,
        token_gateway: TokenEncoder,
        telegram_gateway: InitDataValidator,
        user_gateway: UserManager,
    ) -> None:
        self._db_session = db_session
        self._token_gateway = token_gateway
        self._telegram_gateway = telegram_gateway
        self._user_gateway = user_gateway

    async def __call__(self, data: LoginDTO) -> str | None:
        try:
            valid_data = self._telegram_gateway.validate_telegram_user(data.init_data)
        except Exception:
            return None
        if not valid_data:
            return None

        user_data = valid_data.user
        user_id = user_data["id"]
        user = await self._user_gateway.get_by_id(user_id)
        if not user:
            deposit_comment = generate_deposit_comment()
            user_dm = CreateUserDM(
                id=user_id,
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                deposit_comment=deposit_comment,
            )
            user = await self._user_gateway.save(user_dm)
            await self._db_session.commit()

        referrer_id = self._get_referrer_id(valid_data.start_param)
        if referrer_id and referrer_id != user_id:
            if not await self._user_gateway.get_referrer(user_id):
                await self._user_gateway.add_referral(referrer_id, user)
            else:
                await self._user_gateway.update_referrer(referrer_id, user)
            await self._db_session.commit()

        if user.username != user_data.get("username"):
            await self._user_gateway.update_user(dict(username=user_data.get("username")), id=user_id)
            await self._db_session.commit()
        return self._token_gateway.encode(user_id)

    def _get_referrer_id(self, encoded_payload: str | None) -> int | None:
        try:
            return int(decode_payload(encoded_payload)) if encoded_payload else None
        except Exception:
            return


class GetUserInteractor(Interactor[None, UserDTO]):
    def __init__(
        self,
        user_gateway: UserReader,
        user: UserDM,
        bot_data: BotInfoDM,
    ) -> None:
        self._user_gateway = user_gateway
        self._user = user
        self._bot_data = bot_data

    async def __call__(self) -> UserDTO:
        referral_link = build_direct_link(self._bot_data.username, encode_payload(str(self._user.id)))
        count_referrals = await self._user_gateway.get_count_referrals(self._user.id)
        return UserDTO(
            **self._user.model_dump(), referral_link=referral_link, count_referrals=count_referrals
        )


class GetUserGiftsInteractor:
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, limit: int | None, offset: int | None) -> list[UserGiftDM]:
        return await self._market_gateway.get_user_gifts(self._user.id, limit, offset)


class GetUserGiftInteractor(Interactor[int, UserGiftDM]):
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, gift_id: int) -> UserGiftDM:
        gift = await self._market_gateway.get_user_gift(user_id=self._user.id, gift_id=gift_id)
        if not gift:
            raise NotFoundError("Gift not found")
        return gift


class UpdateUserGiftInteractor:
    def __init__(
        self, market_gateway: OrderSaver, user: UserDM, db_session: DBSession, config: Config
    ) -> None:
        self._market_gateway = market_gateway
        self._user = user
        self._db_session = db_session
        self._config = config

    async def __call__(self, id: int, data: UpdateOrderDTO) -> OrderDM:
        updated_order = await self._market_gateway.update_order(
            data.model_dump(), id=id, is_active=True, is_completed=False, seller_id=self._user.id
        )
        if not updated_order:
            await self._db_session.rollback()
            raise NotFoundError("Gift not found")
        await self._db_session.commit()

        logger.info(
            "UpdateUserGiftInteractor: "
            f"@{self._user.username} #{self._user.id} updated a gift with id: {id}"
        )
        return updated_order


class RemoveOrderInteractor(Interactor[int, None]):
    def __init__(
        self,
        market_gateway: OrderSaver,
        user: UserDM,
        db_session: DBSession,
        user_gateway: UserSaver,
    ) -> None:
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._db_session = db_session

    async def __call__(self, gift_id: int) -> None:
        data = dict(is_active=False, min_step=None, auction_end_time=None, price=None)
        updated_order = await self._market_gateway.update_order(
            data, id=gift_id, is_active=True, is_completed=False, seller_id=self._user.id, buyer_id=None
        )
        if not updated_order:
            await self._db_session.rollback()
            raise NotFoundError("Gift not found")
        await self._market_gateway.delete_auction_bids(gift_id=gift_id)

        await self._db_session.commit()

        logger.info(
            "RemoveOrderInteractor: "
            f"@{self._user.username} #{self._user.id} removed a gift from market with id: {gift_id}"
        )


class WithdrawGiftInteractor(Interactor[int, None]):
    def __init__(
        self,
        market_gateway: OrderSaver,
        user: UserDM,
        db_session: DBSession,
        client: Client,
        bot: Bot,
        config: Config,
    ) -> None:
        self._market_gateway = market_gateway
        self._user = user
        self._db_session = db_session
        self._client = client
        self._bot = bot
        self._config = config

    async def __call__(self, gift_id: int) -> None:
        deleted_order = await self._market_gateway.delete_order(
            id=gift_id, is_active=False, is_completed=False, seller_id=self._user.id
        )
        if not deleted_order:
            await self._db_session.rollback()
            raise NotFoundError("Gift not found")

        is_success = await send_gift(
            self._user.id, deleted_order.gift_id, self._client, self._bot, self._config
        )

        if not is_success:
            await self._db_session.rollback()
            raise GiftSendError("Error when sending a gift")
        await self._db_session.commit()

        logger.info(
            "WithdrawGiftInteractor: "
            f"@{self._user.username} #{self._user.id} withdrew a gift with id: {gift_id}"
        )
