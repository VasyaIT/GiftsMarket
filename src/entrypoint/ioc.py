from typing import AsyncIterable

from dishka import AnyOf, Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.interactors.user import LoginInteractor
from src.application.interfaces.auth import InitDataValidator, TokenDecoder, TokenEncoder
from src.application.interfaces.database import DBSession
from src.entrypoint.config import Config
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.auth import TelegramGateway, TokenGateway
from src.infrastructure.gateways.user import UserGateway


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

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

    user_gateway = provide(UserGateway, scope=Scope.REQUEST)
    login_interactor = provide(LoginInteractor, scope=Scope.REQUEST)
