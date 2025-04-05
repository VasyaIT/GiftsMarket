from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from src.application.common.const import DEFAULT_CHANNEL_IMAGE_URL
from src.application.common.utils import is_subscriber
from src.application.dto.giveaway import CreateGiveawayDTO
from src.application.interactors.errors import (
    GiveawaySubscriptionError,
    NotEnoughBalanceError,
    NotFoundError,
)
from src.application.interfaces.database import DBSession
from src.application.interfaces.giveaway import GiveawayReader, GiveawaySaver
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderManager
from src.application.interfaces.user import UserSaver
from src.domain.entities.giveaway import CreateGiveawayDM, GiveawayDM, TelegramChannelDM
from src.domain.entities.user import UpdateUserBalanceDM, UserDM


class CreateGiveawayInteractor(Interactor[CreateGiveawayDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        giveaway_gateway: GiveawaySaver,
        market_gateway: OrderManager,
        user: UserDM,
        bot: Bot,
    ) -> None:
        self._db_session = db_session
        self._giveaway_gateway = giveaway_gateway
        self._market_gateway = market_gateway
        self._user = user
        self._bot = bot

    async def __call__(self, data: CreateGiveawayDTO) -> None:
        gifts = await self._market_gateway.get_user_gifts_by_ids(data.gifts_ids, self._user.id)
        if not gifts:
            raise NotFoundError("Gifts not found")

        await self._market_gateway.update_giveaway_gifts(
            {"is_completed": True}, [gift.id for gift in gifts]
        )

        create_date = CreateGiveawayDM(**data.model_dump(), user_id=self._user.id)
        await self._giveaway_gateway.save(create_date)

        await self._db_session.commit()


class GiveawayJoinInteractor(Interactor[int, None]):
    def __init__(
        self,
        db_session: DBSession,
        giveaway_gateway: GiveawayReader,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
    ) -> None:
        self._db_session = db_session
        self._giveaway_gateway = giveaway_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot

    async def __call__(self, giveaway_id: int) -> None:
        giveaway = await self._giveaway_gateway.get_one(id=giveaway_id)
        if not giveaway:
            raise NotFoundError("Giveaway not found")

        user = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-giveaway.price)
        )
        if user and user.balance < 0:
            raise NotEnoughBalanceError("User does not have enough balance")

        for channel_username in giveaway.channels_usernames:
            if not await is_subscriber(self._bot, channel_username, self._user.id):
                raise GiveawaySubscriptionError("The conditions of the giveaway are not fulfilled")

        await self._db_session.commit()


class GetAllGiveawaysInteractor(Interactor[str, list[GiveawayDM]]):
    def __init__(self, giveaway_gateway: GiveawayReader, user: UserDM) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._user = user

    async def __call__(self, type: str) -> list[GiveawayDM]:
        return await self._giveaway_gateway.get_many(type, self._user.id)


class GetGiveawayInteractor(Interactor[int, GiveawayDM]):
    def __init__(
        self,
        giveaway_gateway: GiveawayReader,
        user: UserDM,
        bot: Bot,
    ) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._user = user
        self._bot = bot

    async def __call__(self, giveaway_id: int) -> GiveawayDM:
        giveaway = await self._giveaway_gateway.get_one(id=giveaway_id)
        if not giveaway:
            raise NotFoundError("Giveaway not found")
        return giveaway


class TelegramChannelInfoInteractor(Interactor[str, TelegramChannelDM]):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def __call__(self, username: str) -> TelegramChannelDM:
        try:
            channel_info = await self._bot.get_chat(f"@{username}")
        except TelegramAPIError:
            raise NotFoundError("Channel not found")
        image_url = DEFAULT_CHANNEL_IMAGE_URL
        if channel_info.photo:
            file_id = channel_info.photo.small_file_id
            file = await self._bot.get_file(file_id)
            image_url = f"https://api.telegram.org/file/bot{self._bot.token}/{file.file_path}"
        return TelegramChannelDM(
            id=channel_info.id, title=channel_info.title or "", username=username, image_url=image_url
        )
