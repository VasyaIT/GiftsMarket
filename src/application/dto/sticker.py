from pydantic import Field

from src.application.dto.base import BaseDTO


class PackIdDTO(BaseDTO):
    id: int


class BidDTO(BaseDTO):
    id: int
    amount: float = Field(ge=0)
