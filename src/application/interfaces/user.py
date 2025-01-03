from abc import abstractmethod
from typing import Protocol

from src.domain.entities.user import CreateUserDM, UserDM


class UserManager(Protocol):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserDM | None:
        ...

    @abstractmethod
    async def save(self, user: CreateUserDM) -> UserDM:
        ...
