from abc import abstractmethod
from typing import Protocol

from src.domain.entities.auth import InitDataDM


class TokenEncoder(Protocol):
    @abstractmethod
    def encode(self, user_id: int) -> str:
        ...

    @abstractmethod
    def build_payload(self, user_id: int) -> str:
        ...


class TokenDecoder(Protocol):
    @abstractmethod
    def decode(self, encoded_token: str) -> dict:
        ...


class InitDataValidator(Protocol):
    @abstractmethod
    def validate_telegram_user(self, init_data: str) -> InitDataDM | None:
        ...
