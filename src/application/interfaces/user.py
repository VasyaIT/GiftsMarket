from abc import abstractmethod
from typing import Protocol

from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM


class UserReader(Protocol):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserDM | None:
        ...

    async def get_by_comment(self, comment: str) -> UserDM | None:
        ...


class UserSaver(Protocol):
    @abstractmethod
    async def save(self, user: CreateUserDM) -> UserDM:
        ...

    @abstractmethod
    async def update_balance(self, data: UpdateUserBalanceDM) -> UserDM | None:
        ...


class UserManager(UserReader, UserSaver):
    ...
