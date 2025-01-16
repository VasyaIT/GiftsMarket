import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from aiogram import Bot
from aiogram.utils.payload import decode_payload, encode_payload

from src.application.common.const import MINUTES_TO_SEND_GIFT, OrderStatus, PriceList
from src.application.common.utils import build_direct_link, generate_deposit_comment, send_message
from src.application.dto.market import OrderDTO, UpdateOrderDTO
from src.application.dto.star import CreateStarOrderDTO, StarsIdDTO
from src.application.dto.user import LoginDTO, UserDTO
from src.application.interactors import errors
from src.application.interactors.errors import NotAccessError, NotFoundError
from src.application.interfaces.auth import InitDataValidator, TokenEncoder
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderReader, OrderSaver
from src.application.interfaces.star import StarManager, StarOrderReader, StarOrderSaver
from src.application.interfaces.user import UserManager, UserReader, UserSaver
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.market import GetUserGiftsDM, UpdateOrderDM, UserGiftsDM
from src.domain.entities.star import CreateStarOrderDM, StarOrderDM
from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM
from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import stars_order_kb
from src.presentation.bot.services import text


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


class BuyStarsInteractor(Interactor[StarsIdDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
        bot_info: BotInfoDM
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: StarsIdDTO) -> None:
        if not self._user.username:
            raise errors.NotUsernameError("User does not have a username to buy a stars")

        values = dict(status=OrderStatus.BUY, buyer_id=self._user.id)
        order = await self._star_gateway.update(
            values, id=data.id, status=OrderStatus.ON_MARKET, buyer_id=None
        )
        if not order:
            await self._db_session.rollback()
            raise errors.NotFoundError("Order not found")
        if self._user.id == order.seller_id:
            await self._db_session.rollback()
            raise errors.NotAccessError("Forbidden")

        buyer = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(
                id=self._user.id,
                amount=-order.price
            )
        )
        if buyer.balance < 0:  # type: ignore
            await self._db_session.rollback()
            raise errors.NotEnoughBalanceError("User not enough balance")

        await self._db_session.commit()

        direct_link = build_direct_link(self._bot_info.username, f"star_{data.id}")
        await send_message(
            self._bot,
            text.get_buy_stars_text(order.amount),
            [order.seller_id],
            reply_markup=stars_order_kb(order.amount, direct_link)
        )

        logger.info(
            "BuyStarsInteractor: "
            f"@{self._user.username} #{self._user.id} buy the stars with id: {data.id}"
        )


class CancelStarOrderInteractor(Interactor[StarsIdDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
        bot_info: BotInfoDM
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: StarsIdDTO) -> None:
        values = dict(status=OrderStatus.ON_MARKET, buyer_id=None)
        order = await self._star_gateway.update(
            values, id=data.id, status=OrderStatus.BUY, buyer_id=self._user.id
        )

        if not order:
            await self._db_session.rollback()
            raise errors.NotFoundError("Order not found")

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(
                id=self._user.id,
                amount=order.price
            )
        )

        await self._db_session.commit()

        await send_message(
            self._bot,
            text.get_cancel_star_text(order.amount),
            [order.seller_id],
        )

        logger.info(
            "CancelStarOrderInteractor: "
            f"Buyer @{self._user.username} #{self._user.id} cancel the stars order with id: {data.id}"
        )


class SellerAcceptStarOrderInteractor(Interactor[StarsIdDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
        bot_info: BotInfoDM
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: StarsIdDTO) -> None:
        values = dict(status=OrderStatus.SELLER_ACCEPT, created_order_date=datetime.now())
        order = await self._star_gateway.update(
            values, id=data.id, status=OrderStatus.BUY, seller_id=self._user.id
        )

        if not order:
            await self._db_session.rollback()
            raise errors.NotFoundError("Order not found")
        if not order.buyer_id:
            await self._db_session.rollback()
            logger.error(
                "SellerAcceptStarOrderInteractor: "
                f"Buyer not found in seller accept. Stars order id: {data.id}. Seller id: {order.seller_id}"
            )
            raise errors.NotFoundError("Buyer not found")

        await self._db_session.commit()

        direct_link = build_direct_link(self._bot_info.username, f"star_{data.id}")
        await send_message(
            self._bot,
            text.get_seller_accept_star_text(order.amount),
            [order.buyer_id],
            reply_markup=stars_order_kb(order.amount, direct_link)
        )

        logger.info(
            "SellerAcceptStarOrderInteractor: "
            f"Seller @{self._user.username} #{self._user.id} accept the stars order with id: {data.id}"
        )


class SellerCancelStarOrderInteractor(Interactor[StarsIdDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarManager,
        user_gateway: UserSaver,
        user: UserDM,
        config: Config,
        bot: Bot,
        bot_info: BotInfoDM
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._config = config
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: StarsIdDTO) -> None:
        order = await self._star_gateway.get_cancel_order(data.id, self._user.id)

        if not order:
            raise errors.NotFoundError("Order not found")

        if (
            order.created_order_date
            and datetime.now() - timedelta(minutes=MINUTES_TO_SEND_GIFT) < order.created_order_date
        ):
            if order.buyer_id == self._user.id:
                raise errors.NotAccessError("Forbidden")
            elif order.seller_id == self._user.id and order.status is OrderStatus.SELLER_ACCEPT:
                raise errors.NotAccessError("Forbidden")
        else:
            await send_message(
                self._bot,
                text.get_seller_canceled_admin_text(order.seller_id),
                [self._config.bot.DEPOSIT_CHAT_ID],
                message_thread_id=self._config.bot.MODERATION_THREAD_ID,
            )

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(
                id=order.buyer_id,
                amount=order.price
            )
        )
        values = dict(status=OrderStatus.ON_MARKET, buyer_id=None, created_order_date=None)
        await self._star_gateway.update(values, id=data.id)

        await self._db_session.commit()

        if order.seller_id == self._user.id:
            await send_message(
                self._bot,
                text.get_seller_cancel_star_text(order.amount),
                [order.buyer_id]  # type: ignore
            )
            logger.info(
                "SellerCancelStarOrderInteractor: "
                f"Seller @{self._user.username} #{self._user.id} canceled the stars order with id: {data.id}"
            )
        else:
            logger.info(
                "SellerCancelStarOrderInteractor: "
                f"Buyer @{self._user.username} #{self._user.id} canceled the stars order with id: {data.id}"
            )


class ConfirmStarOrderInteractor(Interactor[StarsIdDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
        bot_info: BotInfoDM
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: StarsIdDTO) -> None:
        values = dict(status=OrderStatus.GIFT_TRANSFERRED)
        order = await self._star_gateway.update(
            values, id=data.id, status=OrderStatus.SELLER_ACCEPT, seller_id=self._user.id
        )
        if not (order and order.buyer_id):
            await self._db_session.rollback()
            if not order:
                raise errors.NotFoundError("Order not found")
            elif not order.buyer_id:
                logger.error(
                    "ConfirmStarOrderInteractor: "
                    f"Buyer not found. Stars order id: {data.id}. Seller id: {order.seller_id}"
                )
                raise errors.NotFoundError("Buyer not found")

        await self._db_session.commit()

        direct_link = build_direct_link(self._bot_info.username, f"star_{data.id}")
        await send_message(
            self._bot,
            text.get_confirm_transfer_stars_text(order.amount),
            [order.buyer_id],
            reply_markup=stars_order_kb(order.amount, direct_link)
        )

        logger.info(
            "ConfirmStarOrderInteractor: "
            f"Seller @{self._user.username} #{self._user.id} confirmed the transfer stars id: {data.id}"
        )


class AcceptTransferStarOrderInteractor(Interactor[StarsIdDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        star_gateway: StarOrderSaver,
        user_gateway: UserManager,
        user: UserDM,
        config: Config,
        bot: Bot,
        bot_info: BotInfoDM
    ) -> None:
        self._db_session = db_session
        self._star_gateway = star_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._config = config
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: StarsIdDTO) -> None:
        values = dict(status=OrderStatus.GIFT_RECEIVED, completed_order_date=datetime.now())
        order = await self._star_gateway.update(
            values, id=data.id, status=OrderStatus.GIFT_TRANSFERRED, buyer_id=self._user.id
        )

        if not order:
            await self._db_session.rollback()
            raise errors.NotFoundError("Order not found")

        commission = order.price * PriceList.SELLER_FEE_PERCENT / 100
        if order.seller_id in self._config.bot.nft_holders_id:
            commission = 0
        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=order.seller_id, amount=order.price - commission)
        )
        referrer = await self._user_gateway.get_referrer(user_id=order.seller_id)
        if referrer:
            referrer_percent = PriceList.REFERRAL_PERCENT
            if referrer.id in self._config.app.vip_users_id:
                referrer_percent = PriceList.VIP_REFERRAL_PERCENT
            referrer_reward = commission * referrer_percent / 100
            await self._user_gateway.update_referrer_balance(referrer.id, referrer_reward)
        await self._db_session.commit()

        direct_link = build_direct_link(self._bot_info.username, f"star_{data.id}")
        await send_message(
            self._bot,
            text.get_accept_transfer_stars_text(order.amount),
            [order.buyer_id, order.seller_id],  # type: ignore
            reply_markup=stars_order_kb(order.amount, direct_link)
        )

        logger.info(
            "AcceptTransferStarOrderInteractor: "
            f"Stars order id: {data.id} successfully completed"
        )


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
