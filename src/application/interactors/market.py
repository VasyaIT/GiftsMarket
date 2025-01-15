import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from aiogram import Bot

from src.application.common.const import (
    MINUTES_TO_SEND_GIFT,
    GiftRarity,
    GiftType,
    OrderStatus,
    OrderType,
    PriceList
)
from src.application.common.utils import send_message
from src.application.dto.market import CreateOrderDTO
from src.application.interactors import errors
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderManager, OrderReader, OrderSaver
from src.application.interfaces.user import UserManager, UserSaver
from src.domain.entities.market import (
    CreateOrderDM,
    GiftFiltersDM,
    OrderDM,
    OrderFiltersDM,
    ReadOrderDM
)
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.entrypoint.config import Config
from src.presentation.api.market.params import GiftFilterParams, GiftSortParams, OrderFilterParams
from src.presentation.bot.services import text


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    filename="src/logs/market.log",
    maxBytes=1 * 1024 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
logger.addHandler(handler)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


class CreateOrderInteractor(Interactor[CreateOrderDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        user: UserDM,
        user_gateway: UserSaver,
        config: Config,
        bot: Bot,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user = user
        self._user_gateway = user_gateway
        self._config = config
        self._bot = bot

    async def __call__(self, data: CreateOrderDTO) -> None:
        if not self._config.app.DEBUG and not data.image_url.startswith(self._config.bot.WEBAPP_URL):
            raise errors.InvalidImageUrlError("This image does not exist for a gift")
        if not self._user.username:
            raise errors.NotUsernameError("User does not have a username to create an order")

        if await self._market_gateway.is_exist(type=data.type, number=data.number):
            raise errors.AlreadyExistError("Order already exist")

        await self._market_gateway.save(
            CreateOrderDM(**data.model_dump(), seller_id=self._user.id)
        )
        if self._user.id not in self._config.bot.nft_holders_id:
            updated_user = await self._user_gateway.update_balance(
                UpdateUserBalanceDM(id=self._user.id, amount=-PriceList.UP_FOR_SALE)
            )
            if not updated_user or updated_user.balance < 0:
                await self._db_session.rollback()
                raise errors.NotEnoughBalanceError("User does not have enough balance")
        await self._db_session.commit()

        logger.info(
            "CreateOrderInteractor: "
            f"@{self._user.username} #{self._user.id} created the order"
        )


class GetGiftsInteractor:
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, data: GiftFilterParams, sort_by: GiftSortParams | None) -> list[ReadOrderDM]:
        filters = self._prepare_filters(data, self._user.id)
        return await self._market_gateway.get_all_gifts(filters, sort_by)

    def _prepare_filters(self, filters: GiftFilterParams, user_id: int) -> GiftFiltersDM:
        return GiftFiltersDM(
            limit=filters.limit,
            offset=filters.offset,
            from_price=filters.from_price if filters.from_price else 0,
            to_price=filters.to_price if filters.to_price else 99999,
            rarities=filters.rarities if filters.rarities else [rarity for rarity in GiftRarity],
            types=filters.types if filters.types else [type for type in GiftType],
            status=OrderStatus.ON_MARKET,
            user_id=user_id,
        )


class GetGiftInteractor(Interactor[int, ReadOrderDM]):
    def __init__(self, market_gateway: OrderReader) -> None:
        self._market_gateway = market_gateway

    async def __call__(self, gift_id: int) -> ReadOrderDM:
        gift = await self._market_gateway.get_one(id=gift_id, status=OrderStatus.ON_MARKET)
        if not gift:
            raise errors.NotFoundError("Gift not found")
        return gift


class GetOrdersInteractor(Interactor[OrderFilterParams, list[ReadOrderDM]]):
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, data: OrderFilterParams) -> list[ReadOrderDM]:
        filters = self._prepare_filters(data)
        return await self._market_gateway.get_all_orders(filters)

    def _prepare_filters(self, filters: OrderFilterParams) -> OrderFiltersDM:
        statuses = [OrderStatus.BUY, OrderStatus.SELLER_ACCEPT, OrderStatus.GIFT_TRANSFERRED]
        if filters.order_type is OrderType.ALL:
            statuses.append(OrderStatus.GIFT_RECEIVED)
        elif filters.order_type is OrderType.CLOSED:
            statuses = [OrderStatus.GIFT_RECEIVED]

        return OrderFiltersDM(
            limit=filters.limit,
            offset=filters.offset,
            statuses=statuses,
            user_id=self._user.id,
            is_buyer=filters.order_type is OrderType.BUY,
            is_seller=filters.order_type is OrderType.SELL,
        )


class GetOrderInteractor(Interactor[int, ReadOrderDM]):
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, gift_id: int) -> ReadOrderDM:
        gift = await self._market_gateway.get_by_id_and_user(
            order_id=gift_id,
            user_id=self._user.id,
            statuses=[
                OrderStatus.BUY,
                OrderStatus.SELLER_ACCEPT,
                OrderStatus.GIFT_TRANSFERRED,
                OrderStatus.GIFT_RECEIVED
            ],
        )
        if not gift:
            raise errors.NotFoundError("Gift not found")
        return gift


class BuyGiftInteractor(Interactor[int, OrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot

    async def __call__(self, order_id: int) -> OrderDM:
        if not self._user.username:
            raise errors.NotUsernameError("User does not have a username to buy a gift")

        values = dict(status=OrderStatus.BUY, buyer_id=self._user.id)
        order = await self._market_gateway.update_order(
            values, id=order_id, status=OrderStatus.ON_MARKET, buyer_id=None
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

        await send_message(
            self._bot,
            text.get_buy_gift_text(order.type.name, order.number),
            [order.seller_id]
        )

        logger.info(
            "BuyGiftInteractor: "
            f"@{self._user.username} #{self._user.id} buy the order with id: {order_id}"
        )
        return order


class CancelOrderInteractor(Interactor[int, OrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
        config: Config,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._config = config

    async def __call__(self, order_id: int) -> OrderDM:
        values = dict(status=OrderStatus.ON_MARKET, buyer_id=None)
        order = await self._market_gateway.update_order(
            values, id=order_id, status=OrderStatus.BUY, buyer_id=self._user.id
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
            text.get_cancel_gift_text(order.type.name, order.number),
            [order.seller_id],
        )

        logger.info(
            "CancelOrderInteractor: "
            f"Buyer @{self._user.username} #{self._user.id} cancel the order with id: {order_id}"
        )
        return order


class SellerAcceptInteractor(Interactor[int, OrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderSaver,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot

    async def __call__(self, order_id: int) -> OrderDM:
        values = dict(status=OrderStatus.SELLER_ACCEPT, created_order_date=datetime.now())
        order = await self._market_gateway.update_order(
            values, id=order_id, status=OrderStatus.BUY, seller_id=self._user.id
        )

        if not order:
            await self._db_session.rollback()
            raise errors.NotFoundError("Order not found")
        if not order.buyer_id:
            await self._db_session.rollback()
            logger.error(
                "SellerAcceptInteractor: "
                f"Buyer not found in seller accept. Order id: {order_id}. Seller id: {order.seller_id}"
            )
            raise errors.NotFoundError("Buyer not found")

        await self._db_session.commit()

        await send_message(
            self._bot,
            text.get_seller_accept_text(order.type.name, order.number),
            [order.buyer_id]
        )

        logger.info(
            "SellerAcceptInteractor: "
            f"Seller @{self._user.username} #{self._user.id} accept the order with id: {order_id}"
        )
        return order


class SellerCancelInteractor(Interactor[int, OrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
        config: Config,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._config = config

    async def __call__(self, order_id: int) -> OrderDM:
        order = await self._market_gateway.get_cancel_order(order_id, self._user.id)

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
        await self._market_gateway.update_order(data=values, id=order_id)

        await self._db_session.commit()

        if order.seller_id == self._user.id:
            await send_message(
                self._bot,
                text.get_seller_cancel_text(order.type.name, order.number),
                [order.buyer_id]  # type: ignore
            )
            logger.info(
                "SellerCancelInteractor: "
                f"Seller @{self._user.username} #{self._user.id} canceled the order with id: {order_id}"
            )
        else:
            logger.info(
                "SellerCancelInteractor: "
                f"Buyer @{self._user.username} #{self._user.id} canceled the order with id: {order_id}"
            )
        return order


class ConfirmTransferInteractor(Interactor[int, OrderDM]):
    def __init__(self, db_session: DBSession, market_gateway: OrderSaver, user: UserDM, bot: Bot) -> None:
        self._db_session = db_session
        self._user = user
        self._market_gateway = market_gateway
        self._bot = bot

    async def __call__(self, order_id: int) -> OrderDM:
        values = dict(status=OrderStatus.GIFT_TRANSFERRED)
        order = await self._market_gateway.update_order(
            values, id=order_id, status=OrderStatus.SELLER_ACCEPT, seller_id=self._user.id
        )
        if not (order and order.buyer_id):
            await self._db_session.rollback()
            if not order:
                raise errors.NotFoundError("Order not found")
            elif not order.buyer_id:
                logger.error(
                    "ConfirmTransferInteractor: "
                    f"Buyer not found. Order id: {order_id}. Seller id: {order.seller_id}"
                )
                raise errors.NotFoundError("Buyer not found")

        await self._db_session.commit()

        await send_message(
            self._bot,
            text.get_confirm_transfer_text(order.type.name, order.number),
            [order.buyer_id],
        )

        logger.info(
            "ConfirmTransferInteractor: "
            f"Seller @{self._user.username} #{self._user.id} confirmed the transfer order id: {order_id}"
        )
        return order


class AcceptTransferInteractor(Interactor[int, OrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderSaver,
        user_gateway: UserManager,
        user: UserDM,
        bot: Bot,
        config: Config,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._config = config

    async def __call__(self, order_id: int) -> OrderDM:
        values = dict(status=OrderStatus.GIFT_RECEIVED, completed_order_date=datetime.now())
        order = await self._market_gateway.update_order(
            values, id=order_id, status=OrderStatus.GIFT_TRANSFERRED, buyer_id=self._user.id
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

        await send_message(
            self._bot,
            text.get_accept_transfer_text(order.type.name, order.number),
            [order.buyer_id, order.seller_id]  # type: ignore
        )

        logger.info(
            "AcceptTransferInteractor: "
            f"Order id: {order_id} successfully completed"
        )
        return order
