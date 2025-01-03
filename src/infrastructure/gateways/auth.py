from datetime import datetime
from hashlib import sha256
from hmac import new
from json import loads
from urllib.parse import unquote

import jwt

from src.application.interfaces.auth import TokenDecoder, TokenEncoder
from src.domain.entities.auth import InitDataDM
from src.entrypoint.config import AppConfig, BotConfig
from src.infrastructure.gateways.errors import TokenError


class TokenGateway(TokenEncoder, TokenDecoder):
    def __init__(self, app_config: AppConfig) -> None:
        self.secret_key = app_config.SECRET_KEY
        self.algorithm = app_config.TOKEN_ALGORITHM
        self.lifetime_seconds = app_config.TOKEN_LIFETIME

    def encode(self, user_id: int) -> str:
        payload = self.build_payload(user_id)
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, encoded_token: str) -> dict:
        try:
            payload = jwt.decode(encoded_token, self.secret_key, algorithms=[self.algorithm])
            expired_at = int(payload.get("expired_at"))
        except (jwt.DecodeError, ValueError):
            raise TokenError("Token is invalid")
        if datetime.now().timestamp() > expired_at:
            raise TokenError("Token is expired")
        return payload

    def build_payload(self, user_id: int) -> dict[str, int]:
        expired_at = int(datetime.now().timestamp() + self.lifetime_seconds)
        return {"user_id": user_id, "expired_at": expired_at}


class TelegramGateway:
    def __init__(self, bot_config: BotConfig) -> None:
        self.bot_token = bot_config.BOT_TOKEN

    def validate_telegram_user(self, init_data: str) -> InitDataDM | None:
        data = {value.split("=", 1)[0]: unquote(value.split("=", 1)[1]) for value in init_data.split("&")}
        hash = data.pop("hash")
        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(data.items())
        )
        secret_key = new("WebAppData".encode(), self.bot_token.encode(), sha256).digest()
        calculated_hash = new(secret_key, data_check_string.encode(), sha256).hexdigest()
        if calculated_hash == hash:
            return InitDataDM(user=loads(data.get("user", "")), start_param=data.get("start_param"))
