from abc import abstractmethod
from typing import Protocol

from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM


class UserReader(Protocol):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserDM | None:
        ...

    async def get_referrer(self, user_id: int) -> UserDM | None:
        ...

    async def get_count_referrals(self, user_id: int) -> int:
        ...

    async def get_by_comment(self, comment: str) -> UserDM | None:
        ...


class UserSaver(Protocol):
    @abstractmethod
    async def save(self, user: CreateUserDM) -> UserDM:
        ...

    @abstractmethod
    async def update_user(self, data: dict, **filters) -> UserDM | None:
        ...

    @abstractmethod
    async def update_balance(self, data: UpdateUserBalanceDM) -> UserDM | None:
        ...

    @abstractmethod
    async def update_referrer_balance(self, referrer_id: int, amount: float) -> None:
        ...

    @abstractmethod
    async def add_referral(self, referrer_id: int, referral: UserDM) -> None:
        ...

    @abstractmethod
    async def update_referrer(self, referrer_id: int, referral: UserDM) -> None:
        ...


class UserManager(UserReader, UserSaver):
    ...
