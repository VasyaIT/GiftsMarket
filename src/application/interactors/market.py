import logging

from aiogram import Bot

from src.application.common.const import GiftRarity, OrderStatus, PriceList
from src.application.dto.market import CreateOrderDTO, OrderDTO
from src.application.interactors.errors import NotAccessError, NotEnoughBalanceError, NotFoundError
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderReader, OrderSaver
from src.application.interfaces.user import UserSaver
from src.domain.entities.market import (
    CreateOrderDM,
    GiftFiltersDM,
    OrderDM,
    OrderFiltersDM,
    ReadOrderDM,
    UpdateOrderStatusDM
)
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.entrypoint.config import Config
from src.presentation.api.market.params import GiftFilterParams, OrderFilterParams
from src.presentation.bot.services import text


logger = logging.getLogger(__name__)


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
        sum_characteristics_percent = sum((data.background, data.model, data.pattern))
        rarity = GiftRarity.LEGEND
        if sum_characteristics_percent >= 2.5:
            rarity = GiftRarity.COMMON
        elif sum_characteristics_percent >= 1.7:
            rarity = GiftRarity.RARE
        elif sum_characteristics_percent >= 1:
            rarity = GiftRarity.MYTHICAL

        await self._market_gateway.save(
            CreateOrderDM(
                image_url="",
                type=data.type,
                rarity=rarity,
                price=data.price,
                background=data.background,
                model=data.model,
                pattern=data.pattern,
                seller_id=self._user.id,
            )
        )
        updated_user = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-PriceList.UP_FOR_SALE)
        )
        if not updated_user or updated_user.balance < 0:
            await self._db_session.rollback()
            raise NotEnoughBalanceError("User does not have enough balance")
        await self._db_session.commit()


class GetGiftsInteractor(Interactor[GiftFilterParams, list[ReadOrderDM]]):
    def __init__(self, market_gateway: OrderReader) -> None:
        self._market_gateway = market_gateway

    async def __call__(self, data: GiftFilterParams) -> list[ReadOrderDM]:
        filters = self._prepare_filters(data)
        return await self._market_gateway.get_all_gifts(filters)

    def _prepare_filters(self, filters: GiftFilterParams) -> GiftFiltersDM:
        return GiftFiltersDM(
            limit=filters.limit,
            offset=filters.offset,
            from_price=filters.from_price if filters.from_price else 0,
            to_price=filters.to_price if filters.to_price else 99999,
            rarities=filters.rarities if filters.rarities else [],
            types=filters.types if filters.types else [],
            status=OrderStatus.ON_MARKET
        )


class GetOrdersInteractor(Interactor[OrderFilterParams, list[ReadOrderDM]]):
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, data: OrderFilterParams) -> list[ReadOrderDM]:
        filters = self._prepare_filters(data)
        return await self._market_gateway.get_all_orders(filters)

    def _prepare_filters(self, filters: OrderFilterParams) -> OrderFiltersDM:
        return OrderFiltersDM(
            limit=filters.limit,
            offset=filters.offset,
            statuses=[OrderStatus.BUY, OrderStatus.GIFT_TRANSFERRED]
        )


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
        order_dm = UpdateOrderStatusDM(
            id=order_id,
            current_status=OrderStatus.ON_MARKET,
            new_status=OrderStatus.BUY,
            new_buyer_id=self._user.id
        )
        order = await self._market_gateway.update_status(order_dm, consider_buyers=True)

        if not order:
            await self._db_session.rollback()
            raise NotFoundError("Order not found")
        if self._user.id == order.seller_id:
            await self._db_session.rollback()
            raise NotAccessError("Forbidden")

        buyer = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(
                id=self._user.id,
                amount=-(order.price + PriceList.BUYER_FEE_TON)
            )
        )
        if buyer.balance < 0:  # type: ignore
            await self._db_session.rollback()
            raise NotEnoughBalanceError("User not enough balance")

        await self._db_session.commit()

        await self._bot.send_photo(
            chat_id=order.seller_id,
            photo=order.image_url,
            caption=text.get_buy_gift_text(order.type.name),
        )

        logger.info(f"Order id: {order_id} successfully completed")
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
        order_dm = UpdateOrderStatusDM(
            id=order_id,
            current_status=OrderStatus.BUY,
            new_status=OrderStatus.ON_MARKET,
            current_buyer_id=self._user.id,
            new_buyer_id=None,
        )
        order = await self._market_gateway.update_status(order_dm, consider_buyers=True)

        if not order:
            await self._db_session.rollback()
            raise NotFoundError("Order not found")

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(
                id=self._user.id,
                amount=order.price + PriceList.BUYER_FEE_TON
            )
        )

        await self._db_session.commit()

        await self._bot.send_photo(
            chat_id=order.seller_id,
            photo=order.image_url,
            caption=text.get_cancel_gift_text(order.type.name),
        )
        await self._bot.send_message(
            self._config.bot.DEPOSIT_CHAT_ID,
            text.get_canceled_text_to_owner(self._user.username, self._user.id)
        )

        logger.info(f"Order id: {order_id} was canceled")
        return order


class ConfirmTransferInteractor(Interactor[int, OrderDM]):
    def __init__(self, db_session: DBSession, market_gateway: OrderSaver, user: UserDM, bot: Bot) -> None:
        self._db_session = db_session
        self._user = user
        self._market_gateway = market_gateway
        self._bot = bot

    async def __call__(self, order_id: int) -> OrderDM:
        order = await self._market_gateway.update_status(
            UpdateOrderStatusDM(
                id=order_id,
                current_status=OrderStatus.BUY,
                new_status=OrderStatus.GIFT_TRANSFERRED,
            )
        )
        if not (order and order.buyer_id and order.seller_id == self._user.id):
            await self._db_session.rollback()
            if not order:
                raise NotFoundError("Order not found")
            elif not order.buyer_id:
                logger.error(f"Buyer not found in confirm transfer. Order id: {order_id}")
                raise NotFoundError("Buyer not found")
            elif order.seller_id != self._user.id:
                raise NotAccessError("Forbidden")

        await self._db_session.commit()

        await self._bot.send_photo(
            chat_id=order.buyer_id,
            photo=order.image_url,
            caption=text.get_confirm_transfer_text(order.type.name),
        )
        return order


class AcceptTransferInteractor(Interactor[int, OrderDM]):
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
        order_dm = UpdateOrderStatusDM(
            id=order_id,
            current_status=OrderStatus.GIFT_TRANSFERRED,
            new_status=OrderStatus.GIFT_RECEIVED,
            current_buyer_id=self._user.id,
            new_buyer_id=self._user.id
        )
        order = await self._market_gateway.update_status(order_dm, consider_buyers=True)

        if not order:
            await self._db_session.rollback()
            raise NotFoundError("Order not found")

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(
                id=order.seller_id,
                amount=order.price - (order.price * PriceList.SELLER_FEE_PERCENT / 100)
            )
        )
        await self._db_session.commit()

        for user_id in (order.buyer_id, order.seller_id):
            await self._bot.send_photo(
                chat_id=user_id,  # type: ignore
                photo=order.image_url,
                caption=text.get_accept_transfer_text(order.type.name),
            )
        return order
