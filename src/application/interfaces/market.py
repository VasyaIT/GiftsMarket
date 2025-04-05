from abc import abstractmethod
from typing import Protocol

from src.domain.entities.cart import CartGiftDM
from src.domain.entities.market import (
    BidDM,
    CreateOrderDM,
    GiftFiltersDM,
    OrderDM,
    ReadOrderDM,
    UserGiftDM,
)
from src.presentation.api.market.params import GiftSortParams


class OrderReader(Protocol):
    @abstractmethod
    async def get_all_gifts(
        self, filters: GiftFiltersDM, sort_by: GiftSortParams | None
    ) -> list[OrderDM]: ...

    @abstractmethod
    async def get_user_gifts(
        self, user_id: int, limit: int | None, offset: int | None
    ) -> list[UserGiftDM]: ...

    @abstractmethod
    async def get_user_gift(self, user_id: int, gift_id: int) -> UserGiftDM | None: ...

    @abstractmethod
    async def get_one(self, **filters) -> OrderDM | None: ...

    @abstractmethod
    async def get_full_order(self, **filters) -> ReadOrderDM | None: ...

    @abstractmethod
    async def get_gifts_by_ids(self, gifts_ids: list[int], user_id: int) -> list[CartGiftDM]: ...

    @abstractmethod
    async def get_many(self, **filters) -> list[OrderDM]: ...

    @abstractmethod
    async def get_user_gifts_by_ids(self, gifts_ids: list[int], user_id: int) -> list[UserGiftDM]: ...


class OrderSaver(Protocol):
    @abstractmethod
    async def save(self, order_dm: CreateOrderDM) -> CreateOrderDM: ...

    @abstractmethod
    async def update_order(self, data: dict, **filters) -> OrderDM | None: ...

    @abstractmethod
    async def update_giveaway_gifts(self, data: dict, gifts_ids: list[int]) -> None: ...

    @abstractmethod
    async def delete_order(self, **filters) -> UserGiftDM | None: ...

    @abstractmethod
    async def withdraw_from_market(self, data: dict, **filters) -> UserGiftDM | None: ...

    @abstractmethod
    async def save_auction_bid(self, data: BidDM) -> None: ...

    @abstractmethod
    async def delete_auction_bids(self, **filters) -> None: ...

    @abstractmethod
    async def update_cart_orders(self, values: dict, gifts_ids: list[int], user_id: int) -> None: ...


class OrderManager(OrderReader, OrderSaver): ...
