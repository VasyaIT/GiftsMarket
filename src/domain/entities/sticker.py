from pydantic import BaseModel


class StickerOrderDM(BaseModel):
    id: int
    owner_id: int
    buyer_id: int | None


class CreateStarOrderDM(BaseModel):
    amount: float
    owner_id: int


class NewBidDM(BaseModel):
    id: int
    amount: float
    buyer_id: int


class AuctionDM(StickerOrderDM):
    pack_id: str
    last_bid: float
