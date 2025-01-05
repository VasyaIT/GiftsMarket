from abc import abstractmethod
from typing import Protocol

from src.domain.entities.market import (
    CreateOrderDM,
    GiftFiltersDM,
    OrderDM,
    OrderFiltersDM,
    ReadOrderDM,
    UpdateOrderStatusDM
)


class OrderReader(Protocol):
    @abstractmethod
    async def get_all_gifts(self, filters: GiftFiltersDM) -> list[ReadOrderDM]:
        ...

    @abstractmethod
    async def get_all_orders(self, filters: OrderFiltersDM) -> list[ReadOrderDM]:
        ...

    @abstractmethod
    async def get_by_id(self, order_id: int) -> OrderDM | None:
        ...


class OrderSaver(Protocol):
    @abstractmethod
    async def save(self, order_dm: CreateOrderDM) -> None:
        ...

    @abstractmethod
    async def update_status(
        self, order_dm: UpdateOrderStatusDM, consider_buyers: bool = False
    ) -> OrderDM | None:
        ...
