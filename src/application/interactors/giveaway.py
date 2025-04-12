from asyncio import gather
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from src.application.common.const import DEFAULT_AVATAR_URL, GiveawayType
from src.application.common.utils import is_subscriber
from src.application.dto.giveaway import CreateGiveawayDTO, JoinGiveawayDTO
from src.application.interactors.errors import (
    GiveawaySubscriptionError,
    NotAccessError,
    NotEnoughBalanceError,
    NotFoundError,
)
from src.application.interfaces.database import DBSession
from src.application.interfaces.giveaway import GiveawayManager, GiveawayReader, GiveawaySaver
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderManager, OrderReader
from src.application.interfaces.user import UserReader, UserSaver
from src.domain.entities.giveaway import (
    CreateGiveawayDM,
    FullGiveawayDM,
    GiveawayDM,
    GiveawayParticipantDM,
    TelegramChannelDM,
)
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
        gifts = await self._market_gateway.get_user_gifts_by_ids(
            data.gifts_ids, seller_id=self._user.id, is_active=False
        )
        if not gifts:
            raise NotFoundError("Gifts not found")

        for channel_username in data.channels_usernames:
            if not await is_subscriber(self._bot, f"@{channel_username}", self._bot.id):
                raise GiveawaySubscriptionError(f"Bot not in channel @{channel_username}")

        await self._market_gateway.update_giveaway_gifts(
            {"is_completed": True}, [gift.id for gift in gifts]
        )

        create_date = CreateGiveawayDM(**data.model_dump(), user_id=self._user.id)
        await self._giveaway_gateway.save(create_date)

        await self._db_session.commit()


class GiveawayJoinInteractor(Interactor[JoinGiveawayDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        giveaway_gateway: GiveawayManager,
        user_gateway: UserSaver,
        user: UserDM,
        bot: Bot,
    ) -> None:
        self._db_session = db_session
        self._giveaway_gateway = giveaway_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot

    async def __call__(self, data: JoinGiveawayDTO) -> None:
        giveaway = await self._giveaway_gateway.get_one(id=data.id)
        if not giveaway or giveaway.end_time < datetime.now(tz=timezone.utc):
            raise NotFoundError("Giveaway not found")
        participants_ids = giveaway.participants_ids
        referrers_ids = giveaway.referrers_ids
        if (
            giveaway.user_id == self._user.id
            or giveaway.type is not GiveawayType.SUBSCRIPTION_PAID_TICKET
            and self._user.id in giveaway.participants_ids
        ):
            raise NotAccessError("Forbidden")

        if data.referrer_id:
            referrers_ids.append(data.referrer_id)
        if (
            giveaway.quantity_members
            and len(participants_ids) + data.count_tickets > giveaway.quantity_members
        ):
            raise NotAccessError("There are too many participants")

        if giveaway.price > 0:
            price = data.count_tickets * giveaway.price
            user = await self._user_gateway.update_balance(
                UpdateUserBalanceDM(id=self._user.id, amount=-price)
            )
            if user and user.balance < 0:
                raise NotEnoughBalanceError("User does not have enough balance")

        for channel_username in giveaway.channels_usernames:
            if not await is_subscriber(self._bot, f"@{channel_username}", self._user.id):
                raise GiveawaySubscriptionError("The conditions of the giveaway are not fulfilled")
            participants_ids.append(self._user.id)

        await self._giveaway_gateway.update_giveaway(
            {"participants_ids": participants_ids, "referrers_ids": referrers_ids}, id=giveaway.id
        )

        await self._db_session.commit()


class GetGiveawayParticipantsInteractor(Interactor[int, list[GiveawayParticipantDM]]):
    def __init__(self, giveaway_gateway: GiveawayReader, user_gateway: UserReader) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._user_gateway = user_gateway

    async def __call__(self, giveaway_id: int) -> list[GiveawayParticipantDM]:
        giveaway = await self._giveaway_gateway.get_one(id=giveaway_id)
        if not giveaway:
            raise NotFoundError("Giveaway not found")
        tasks = [self._user_gateway.get_by_id(id) for id in giveaway.participants_ids]
        count_referrers, count_participants = len(giveaway.referrers_ids), len(giveaway.participants_ids)
        participants = await gather(*tasks)
        all_win = len(giveaway.gifts_ids) >= count_participants
        result = []
        for participant in participants:
            if not participant:
                continue
            chance_win = 100 / count_participants
            count_participant_referrals = giveaway.referrers_ids.count(participant.id)
            if count_participant_referrals:
                chance_win += (count_participant_referrals / (4 * count_referrers)) * 100
            chance_win = min(chance_win, 95)
            if all_win:
                chance_win = 100
            result.append(
                GiveawayParticipantDM(
                    photo_url=participant.photo_url,
                    name=participant.first_name,
                    count_referrals=count_participant_referrals,
                    chance_win=chance_win,
                    is_win=participant.id in giveaway.winners_ids,
                ),
            )
        return result


class GetAllGiveawaysInteractor(Interactor[str, list[GiveawayDM]]):
    def __init__(self, giveaway_gateway: GiveawayReader, user: UserDM) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._user = user

    async def __call__(self, type: str) -> list[GiveawayDM]:
        return await self._giveaway_gateway.get_many(type, self._user.id)


class GetGiveawayInteractor(Interactor[int, FullGiveawayDM]):
    def __init__(
        self,
        giveaway_gateway: GiveawayReader,
        market_gateway: OrderReader,
        telegram_channel_interactor: "TelegramChannelInfoInteractor",
    ) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._market_gateway = market_gateway
        self._telegram_channel_interactor = telegram_channel_interactor

    async def __call__(self, giveaway_id: int) -> FullGiveawayDM:
        giveaway = await self._giveaway_gateway.get_one(id=giveaway_id)
        if not giveaway:
            raise NotFoundError("Giveaway not found")

        gifts = await self._market_gateway.get_user_gifts_by_ids(giveaway.gifts_ids)
        tasks = [self._telegram_channel_interactor(username) for username in giveaway.channels_usernames]
        channels = await gather(*tasks)
        return FullGiveawayDM(**giveaway.__dict__, gifts=gifts, channels=channels)


class TelegramChannelInfoInteractor(Interactor[str, TelegramChannelDM]):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def __call__(self, username: str) -> TelegramChannelDM:
        try:
            channel_info = await self._bot.get_chat(f"@{username}")
        except TelegramAPIError:
            raise NotFoundError("Channel not found")
        image_url = DEFAULT_AVATAR_URL
        if channel_info.photo:
            file_id = channel_info.photo.small_file_id
            file = await self._bot.get_file(file_id)
            image_url = f"https://api.telegram.org/file/bot{self._bot.token}/{file.file_path}"
        return TelegramChannelDM(
            id=channel_info.id, title=channel_info.title or "", username=username, image_url=image_url
        )
