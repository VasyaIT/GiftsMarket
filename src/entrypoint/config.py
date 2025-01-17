from os import environ

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    CORS_ALLOWED_ORIGINS: str
    DEBUG: bool
    SECRET_KEY: str
    TOKEN_ALGORITHM: str = Field(default="HS256")
    TOKEN_LIFETIME: int = Field(default=86400)
    VIP_USERS_ID: str
    DB_DUMP_FILE_PATH: str

    @property
    def cors_allowed_origins(self) -> list[str]:
        return self.CORS_ALLOWED_ORIGINS.split()

    @property
    def docs_url(self) -> str:
        return "/docs" if self.DEBUG else ""

    @property
    def openapi_url(self) -> str:
        return "/openapi.json" if self.DEBUG else ""

    @property
    def vip_users_id(self) -> list[int]:
        return list(map(int, self.VIP_USERS_ID.split()))


class PostgresConfig(BaseModel):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?async_fallback=True"
        )


class BotConfig(BaseModel):
    BOT_TOKEN: str
    WEBAPP_URL: str
    CHANNEL_ID: str
    DEPOSIT_CHAT_ID: str
    MODERATION_THREAD_ID: int
    OWNERS_CHAT_ID: str
    MODERATORS_CHAT_ID: str
    NFT_HOLDERS_ID: str
    API_ID: int
    API_HASH: str

    @property
    def owners_chat_id(self) -> list[int]:
        return list(map(int, self.OWNERS_CHAT_ID.split()))

    @property
    def moderators_chat_id(self) -> list[int]:
        return list(map(int, self.MODERATORS_CHAT_ID.split()))

    @property
    def nft_holders_id(self) -> list[int]:
        return list(map(int, self.NFT_HOLDERS_ID.split()))


class TonapiConfig(BaseModel):
    TONAPI_TOKEN: str
    DEPOSIT_ADDRESS: str
    IS_TESTNET: bool
    WALLET_MNEMONICS: str


class Config(BaseModel):
    app: AppConfig = Field(default_factory=lambda: AppConfig(**environ))  # type: ignore
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig(**environ))  # type: ignore
    bot: BotConfig = Field(default_factory=lambda: BotConfig(**environ))  # type: ignore
    tonapi: TonapiConfig = Field(default_factory=lambda: TonapiConfig(**environ))  # type: ignore
