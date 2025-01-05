from abc import abstractmethod
from typing import Protocol

from src.domain.entities.market import CreateOrderDM, OrderDM, OrderFiltersDM, UpdateOrderStatusDM


class OrderReader(Protocol):
    @abstractmethod
    async def get_all(self, filters: OrderFiltersDM) -> list[OrderDM]:
        ...

    @abstractmethod
    async def get_by_id(self, order_id: int) -> OrderDM | None:
        ...


class OrderSaver(Protocol):
    @abstractmethod
    async def save(self, order_dm: CreateOrderDM) -> None:
        ...

    @abstractmethod
    async def update_status(self, order_dm: UpdateOrderStatusDM) -> OrderDM | None:
        ...
