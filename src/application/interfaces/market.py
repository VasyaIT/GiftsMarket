from abc import abstractmethod
from typing import Protocol

from src.domain.entities.market import CreateOrderDM, OrderDM


class OrderReader(Protocol):
    @abstractmethod
    async def get_all(self, offset: int | None = 0, limit: int | None = None) -> list[OrderDM]:
        ...


class OrderSaver(Protocol):
    @abstractmethod
    async def save(self, order_dm: CreateOrderDM) -> None:
        ...
