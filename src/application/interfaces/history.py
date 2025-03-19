from abc import abstractmethod
from typing import Protocol

from src.domain.entities.history import CreateHistoryDM, HistoryDM


class HistorySaver(Protocol):
    @abstractmethod
    async def save(self, data: CreateHistoryDM) -> HistoryDM:
        ...

    @abstractmethod
    async def save_many(self, data: list[CreateHistoryDM]) -> None:
        ...


class HistoryReader(Protocol):
    @abstractmethod
    async def get_many(self, **filters) -> list[HistoryDM]:
        ...
