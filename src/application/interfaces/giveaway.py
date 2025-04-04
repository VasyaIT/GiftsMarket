from abc import abstractmethod
from typing import Protocol

from src.domain.entities.giveaway import CreateGiveawayDM, GiveawayDM


class GiveawaySaver(Protocol):
    @abstractmethod
    async def save(self, data: CreateGiveawayDM) -> GiveawayDM: ...


class GiveawayReader(Protocol):
    @abstractmethod
    async def get_one(self, **filters) -> GiveawayDM | None: ...


class GiveawayManager(GiveawaySaver, GiveawayReader): ...
