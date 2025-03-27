import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from aiogram import Bot
from pyrogram.client import Client

from src.application.common.const import MAX_GIFT_NUMBER, GiftRarity, GiftType, HistoryType, PriceList
from src.application.common.send_gift import send_gift
from src.application.common.utils import build_direct_link, send_message
from src.application.dto.market import BidDTO, CreateOrderDTO
from src.application.interactors import errors
from src.application.interfaces.database import DBSession
from src.application.interfaces.history import HistorySaver
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderManager, OrderReader
from src.application.interfaces.user import UserSaver
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.history import CreateHistoryDM
from src.domain.entities.market import BidDM, BidSuccessDM, GiftFiltersDM, OrderDM, ReadOrderDM
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.entrypoint.config import Config
from src.presentation.api.market.params import GiftFilterParams, GiftSortParams
from src.presentation.bot.keyboards.base import order_kb
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
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user = user
        self._user_gateway = user_gateway
        self._config = config

    async def __call__(self, data: CreateOrderDTO) -> None:
        if not data.min_step and data.auction_end_time or data.min_step and not data.auction_end_time:
            raise errors.AuctionBidError("Auction parameters is invalid")
        order = await self._market_gateway.update_order(
            {
                "price": data.price,
                "is_vip": data.is_vip,
                "is_active": True,
                "min_step": data.min_step,
                "auction_end_time": data.auction_end_time,
            },
            id=data.gift_id,
            seller_id=self._user.id,
        )
        if not order:
            raise errors.NotAccessError("Gift not found")

        amount = 0
        if self._user.id not in self._config.bot.nft_holders_id:
            amount = PriceList.UP_FOR_SALE
        amount = PriceList.VIP_ORDER if data.is_vip else amount
        if amount:
            updated_user = await self._user_gateway.update_balance(
                UpdateUserBalanceDM(id=self._user.id, amount=-amount)
            )
            if not updated_user or updated_user.balance < 0:
                await self._db_session.rollback()
                raise errors.NotEnoughBalanceError("User does not have enough balance")

        if data.min_step:
            await self._market_gateway.save_auction_bid(
                BidDM(gift_id=data.gift_id, amount=data.price, buyer_id=self._user.id)
            )
        await self._db_session.commit()

        logger.info(f"CreateOrderInteractor: @{self._user.username} #{self._user.id} created the order")


class GetGiftsInteractor:
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, data: GiftFilterParams, sort_by: GiftSortParams | None) -> list[OrderDM]:
        filters = self._prepare_filters(data, self._user.id)
        return await self._market_gateway.get_all_gifts(filters, sort_by)

    def _prepare_filters(self, filters: GiftFilterParams, user_id: int) -> GiftFiltersDM:
        return GiftFiltersDM(
            limit=filters.limit,
            offset=filters.offset,
            from_price=filters.from_price if filters.from_price else 0,
            to_price=filters.to_price if filters.to_price else 99999,
            from_gift_number=filters.from_gift_number if filters.from_gift_number else 1,
            to_gift_number=filters.to_gift_number if filters.to_gift_number else MAX_GIFT_NUMBER,
            rarities=filters.rarities if filters.rarities else [rarity for rarity in GiftRarity],
            types=filters.types if filters.types else [type for type in GiftType],
            user_id=user_id,
        )


class GetGiftInteractor(Interactor[int, ReadOrderDM]):
    def __init__(self, market_gateway: OrderReader) -> None:
        self._market_gateway = market_gateway

    async def __call__(self, gift_id: int) -> ReadOrderDM:
        gift = await self._market_gateway.get_full_order(id=gift_id, is_active=True, is_completed=False)
        if not gift:
            raise errors.NotFoundError("Gift not found")
        return gift


class BuyGiftInteractor(Interactor[int, OrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        user_gateway: UserSaver,
        history_gateway: HistorySaver,
        user: UserDM,
        bot: Bot,
        bot_info: BotInfoDM,
        config: Config,
        client: Client,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._history_gateway = history_gateway
        self._user = user
        self._bot = bot
        self._bot_info = bot_info
        self._config = config
        self._client = client

    async def __call__(self, gift_id: int) -> OrderDM:
        order = await self._market_gateway.get_one(id=gift_id, is_completed=False, is_active=True)

        if not order:
            raise errors.NotFoundError("Gift not found")
        if self._user.id == order.seller_id:
            raise errors.NotAccessError("Forbidden")
        if order.min_step is not None:
            raise errors.NotAccessError("This gift on auction")

        buyer = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-order.price)
        )
        if buyer.balance < 0:  # type: ignore
            await self._db_session.rollback()
            raise errors.NotEnoughBalanceError("User not enough balance")

        is_success = await send_gift(self._user.id, gift_id, self._client, self._bot, self._config)
        if not is_success:
            await self._db_session.rollback()
            raise errors.GiftSendError("Error when sending a gift")

        await self._db_session.commit()

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=order.seller_id, amount=order.price)
        )
        values = dict(buyer_id=self._user.id, is_completed=True, completed_order_date=datetime.now())
        await self._market_gateway.update_order(
            values, id=gift_id, buyer_id=self._user.id, is_completed=False, is_active=True
        )
        await self._db_session.commit()

        buyer_history_data = CreateHistoryDM(
            user_id=self._user.id,
            type=HistoryType.BUY_GIFT,
            price=order.price,
            gift=order.type,
            model_name=order.model_name,
        )
        seller_history_data = CreateHistoryDM(
            user_id=order.seller_id,
            type=HistoryType.SELL_GIFT,
            price=order.price,
            gift=order.type,
            model_name=order.model_name,
        )
        await self._history_gateway.save_many([buyer_history_data, seller_history_data])
        await self._db_session.commit()

        direct_link = build_direct_link(self._bot_info.username, f"order_{order.id}")
        await send_message(
            self._bot,
            text.get_buy_gift_text(order.type.name, order.number),
            [order.seller_id],
            reply_markup=order_kb(order.type, order.number, direct_link),
        )

        logger.info(
            "BuyGiftInteractor: "
            f"@{self._user.username} #{self._user.id} buy the order with id: {gift_id}"
        )
        return order


class NewBidInteractor(Interactor[BidDTO, BidSuccessDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        user: UserDM,
        user_gateway: UserSaver,
        history_gateway: HistorySaver,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user = user
        self._user_gateway = user_gateway
        self._history_gateway = history_gateway

    async def __call__(self, data: BidDTO) -> BidSuccessDM:
        if not (
            order := await self._market_gateway.get_one(id=data.id, is_completed=False, is_active=True)
        ):
            raise errors.NotFoundError("Gift not found")
        if not order.min_step or order.min_step > data.amount - order.price + 0.01:
            raise errors.AuctionBidError("Amount is too low or this gift not on auction")
        if order.auction_end_time and order.auction_end_time < datetime.now(tz=timezone.utc):
            raise errors.AuctionBidError("Auction already ended")
        if self._user.balance < data.amount:
            raise errors.NotEnoughBalanceError("User does not have enough balance")

        new_balance = self._user.balance - data.amount
        if order.buyer_id == self._user.id:
            new_balance += order.price

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-data.amount)
        )
        if order.buyer_id:
            await self._user_gateway.update_balance(
                UpdateUserBalanceDM(id=order.buyer_id, amount=order.price)
            )

        updated_data = {"buyer_id": self._user.id, "price": data.amount}
        await self._market_gateway.update_order(updated_data, id=data.id)
        await self._market_gateway.save_auction_bid(
            BidDM(gift_id=data.id, amount=data.amount, buyer_id=self._user.id)
        )
        history_data = CreateHistoryDM(
            user_id=self._user.id,
            type=HistoryType.BID_GIFT,
            price=data.amount,
            gift=order.type,
            model_name=order.model_name,
        )
        await self._history_gateway.save(history_data)
        await self._db_session.commit()
        return BidSuccessDM(user_balance=new_balance, created_at=datetime.now(tz=timezone.utc))
