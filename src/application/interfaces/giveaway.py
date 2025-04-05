from abc import abstractmethod
from typing import Protocol

from src.domain.entities.giveaway import CreateGiveawayDM, GiveawayDM


class GiveawaySaver(Protocol):
    @abstractmethod
    async def save(self, data: CreateGiveawayDM) -> GiveawayDM: ...


class GiveawayReader(Protocol):
    @abstractmethod
    async def get_one(self, **filters) -> GiveawayDM | None: ...

    @abstractmethod
    async def get_many(self, type: str, user_id: int) -> list[GiveawayDM]: ...


class GiveawayManager(GiveawaySaver, GiveawayReader): ...
