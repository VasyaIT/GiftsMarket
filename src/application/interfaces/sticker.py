from abc import abstractmethod
from typing import Protocol

from src.domain.entities.sticker import AuctionDM, NewBidDM, StickerOrderDM


class AuctionReader(Protocol):
    @abstractmethod
    async def get_all(self, **filters) -> list[AuctionDM]:
        ...

    @abstractmethod
    async def get_one(self, **filters) -> AuctionDM | None:
        ...


class AuctionSaver(Protocol):
    @abstractmethod
    async def new_bid(self, data: NewBidDM) -> StickerOrderDM | None:
        ...
