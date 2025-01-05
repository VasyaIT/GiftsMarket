from abc import abstractmethod
from typing import Protocol

from src.domain.entities.wallet import CreateWithdrawRequestDM, WithdrawRequestDM


class WithdrawRequestSaver(Protocol):
    @abstractmethod
    async def save(self, data: CreateWithdrawRequestDM) -> WithdrawRequestDM:
        ...

    @abstractmethod
    async def set_completed(self, request_id: int) -> None:
        ...
