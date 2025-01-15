from abc import abstractmethod
from typing import Protocol

from src.application.common.const import OrderStatus
from src.domain.entities.market import (
    CreateOrderDM,
    GetUserGiftsDM,
    GiftFiltersDM,
    OrderDM,
    OrderFiltersDM,
    ReadOrderDM,
    UserGiftsDM
)
from src.presentation.api.market.params import GiftSortParams


class OrderReader(Protocol):
    @abstractmethod
    async def get_all_gifts(self, filters: GiftFiltersDM, sort_by: GiftSortParams | None) -> list[ReadOrderDM]:
        ...

    @abstractmethod
    async def get_all_orders(self, filters: OrderFiltersDM) -> list[ReadOrderDM]:
        ...

    @abstractmethod
    async def get_user_gifts(self, data: GetUserGiftsDM) -> list[UserGiftsDM]:
        ...

    @abstractmethod
    async def get_one(self, **filters) -> ReadOrderDM | None:
        ...

    @abstractmethod
    async def is_exist(self, **filters) -> bool:
        ...

    @abstractmethod
    async def get_by_id_and_user(
        self, order_id: int, user_id: int, statuses: list[OrderStatus]
    ) -> ReadOrderDM | None:
        ...

    @abstractmethod
    async def get_cancel_order(self, order_id: int, user_id: int) -> OrderDM | None:
        ...


class OrderSaver(Protocol):
    @abstractmethod
    async def save(self, order_dm: CreateOrderDM) -> OrderDM:
        ...

    @abstractmethod
    async def update_order(self, data: dict, **filters) -> OrderDM | None:
        ...

    @abstractmethod
    async def seller_cancel_order(self, order_id: int, user_id: int, data: dict) -> OrderDM | None:
        ...

    @abstractmethod
    async def delete_order(self, **filters) -> OrderDM | None:
        ...


class OrderManager(OrderReader, OrderSaver):
    ...
