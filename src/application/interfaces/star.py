from abc import abstractmethod
from typing import Protocol

from src.domain.entities.star import CreateStarOrderDM, StarOrderDM
from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM


class StarOrderReader(Protocol):
    @abstractmethod
    async def get_one(self, **filters) -> StarOrderDM:
        ...


class StarOrderSaver(Protocol):
    @abstractmethod
    async def save(self, star_order: CreateStarOrderDM) -> None:
        ...

    @abstractmethod
    async def update(self, values: dict, **filters) -> StarOrderDM | None:
        ...

    @abstractmethod
    async def delete(self, **filters) -> StarOrderDM | None:
        ...
