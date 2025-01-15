from typing import AsyncIterable

from aiogram import Bot
from dishka import AnyOf, Scope, from_context, provide
from dishka.integrations.fastapi import FastapiProvider
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.common.fixtures import get_gift_images
from src.application.dto.common import GiftImagesDTO
from src.application.interactors import market, user
from src.application.interactors.star import CreateStarOrderInteractor
from src.application.interactors.wallet import WithdrawRequestInteractor
from src.application.interfaces.auth import InitDataValidator, TokenDecoder, TokenEncoder
from src.application.interfaces.database import DBSession
from src.application.interfaces.market import OrderManager, OrderReader, OrderSaver
from src.application.interfaces.star import StarOrderReader, StarOrderSaver
from src.application.interfaces.user import UserManager, UserReader, UserSaver
from src.application.interfaces.wallet import WithdrawRequestSaver
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.user import UserDM
from src.entrypoint.config import Config
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.auth import TelegramGateway, TokenGateway
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.gateways.star import StarGateway
from src.infrastructure.gateways.user import UserGateway
from src.infrastructure.gateways.wallet import WalletGateway
from src.presentation.api.authentication import get_user_by_token


class AppProvider(FastapiProvider):
    config = from_context(provides=Config, scope=Scope.APP)
    bot = from_context(provides=Bot, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def bot_info(self, bot: Bot) -> BotInfoDM:
        bot_data = await bot.me()
        return BotInfoDM(**bot_data.model_dump())

    @provide(scope=Scope.APP)
    async def get_image_fixtures(self, config: Config) -> GiftImagesDTO:
        return get_gift_images(config.bot.WEBAPP_URL)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def authentication(
        self, request: Request, user_gateway: UserReader, token_gateway: TokenDecoder
    ) -> UserDM:
        return await get_user_by_token(request, user_gateway, token_gateway)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AnyOf[
        AsyncSession,
        DBSession,
    ]]:
        async with session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @provide(scope=Scope.REQUEST, provides=AnyOf[TokenEncoder, TokenDecoder])
    async def get_token_gateway(self, config: Config) -> TokenGateway:
        return TokenGateway(app_config=config.app)

    @provide(scope=Scope.REQUEST, provides=AnyOf[InitDataValidator])
    async def get_telegram_gateway(self, config: Config) -> TelegramGateway:
        return TelegramGateway(bot_config=config.bot)

    user_gateway = provide(
        UserGateway, scope=Scope.REQUEST, provides=AnyOf[UserManager, UserReader, UserSaver]
    )
    market_gateway = provide(
        MarketGateway, scope=Scope.REQUEST, provides=AnyOf[OrderManager, OrderSaver, OrderReader]
    )
    wallet_gateway = provide(WalletGateway, scope=Scope.REQUEST, provides=AnyOf[WithdrawRequestSaver])
    star_gateway = provide(
        StarGateway, scope=Scope.REQUEST, provides=AnyOf[StarOrderReader, StarOrderSaver]
    )

    login_interactor = provide(user.LoginInteractor, scope=Scope.REQUEST)
    get_user_interactor = provide(user.GetUserInteractor, scope=Scope.REQUEST)
    get_user_gifts_interactor = provide(user.GetUserGiftsInteractor, scope=Scope.REQUEST)
    get_user_gift_interactor = provide(user.GetUserGiftInteractor, scope=Scope.REQUEST)
    update_user_gift_interactor = provide(user.UpdateUserGiftInteractor, scope=Scope.REQUEST)
    delete_user_gift_interactor = provide(user.DeleteUserGiftInteractor, scope=Scope.REQUEST)
    create_order_interactor = provide(market.CreateOrderInteractor, scope=Scope.REQUEST)
    buy_gift_interactor = provide(market.BuyGiftInteractor, scope=Scope.REQUEST)
    cancel_order_interactor = provide(market.CancelOrderInteractor, scope=Scope.REQUEST)
    seller_accept_interactor = provide(market.SellerAcceptInteractor, scope=Scope.REQUEST)
    seller_cancel_interactor = provide(market.SellerCancelInteractor, scope=Scope.REQUEST)
    confirm_transfer_interactor = provide(market.ConfirmTransferInteractor, scope=Scope.REQUEST)
    accept_transfer_interactor = provide(market.AcceptTransferInteractor, scope=Scope.REQUEST)
    get_gifts_interactor = provide(market.GetGiftsInteractor, scope=Scope.REQUEST)
    get_gift_interactor = provide(market.GetGiftInteractor, scope=Scope.REQUEST)
    get_orders_interactor = provide(market.GetOrdersInteractor, scope=Scope.REQUEST)
    get_order_interactor = provide(market.GetOrderInteractor, scope=Scope.REQUEST)
    withdraw_request_interactor = provide(WithdrawRequestInteractor, scope=Scope.REQUEST)
    create_star_interactor = provide(CreateStarOrderInteractor, scope=Scope.REQUEST)
