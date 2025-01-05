from aiogram.utils.payload import decode_payload, encode_payload

from src.application.common.utils import generate_deposit_comment
from src.application.dto.user import LoginDTO, UserDTO
from src.application.interfaces.auth import InitDataValidator, TokenEncoder
from src.application.interfaces.database import DBSession
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.user import UserManager
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.user import CreateUserDM, UserDM


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
                if await self._user_gateway.add_referral(referrer_id, user):
                    await self._db_session.commit()
                else:
                    await self._db_session.rollback()
        return self._token_gateway.encode(user_id)

    def _get_referrer_id(self, decoded_payload: str | None) -> int | None:
        try:
            return None if not decoded_payload else int(decode_payload(decoded_payload))
        except Exception:
            return


class GetUserInteractor(Interactor[None, UserDTO]):
    def __init__(
        self,
        user: UserDM,
        bot_data: BotInfoDM,
    ) -> None:
        self._user = user
        self._bot_data = bot_data

    async def __call__(self) -> UserDTO:
        payload = encode_payload(str(self._user.id))
        referral_link = f"https://t.me/{self._bot_data.username}/market?startapp={payload}"
        return UserDTO(**self._user.model_dump(), referral_link=referral_link)
