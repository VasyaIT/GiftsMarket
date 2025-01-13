from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.wallet import WithdrawRequestSaver
from src.domain.entities.wallet import CreateWithdrawRequestDM, WithdrawRequestDM
from src.infrastructure.models.transaction import WithdrawRequest


class WalletGateway(WithdrawRequestSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, data: CreateWithdrawRequestDM) -> WithdrawRequestDM:
        stmt = insert(WithdrawRequest).values(data.model_dump()).returning(WithdrawRequest)
        result = await self._session.execute(stmt)
        return WithdrawRequestDM(**result.scalar_one().__dict__)

    async def set_completed(self, request_id: int) -> WithdrawRequestDM | None:
        stmt = (
            update(WithdrawRequest)
            .filter_by(id=request_id, is_completed=False)
            .values(is_completed=True)
            .returning(WithdrawRequest)
        )
        result = await self._session.execute(stmt)
        withdraw_request = result.scalar_one_or_none()
        if withdraw_request:
            return WithdrawRequestDM(**withdraw_request.__dict__)

    async def get_by_user_id(self, user_id: int) -> tuple[list[WithdrawRequestDM], float]:
        stmt = select(WithdrawRequest).filter_by(user_id=user_id)
        result = await self._session.execute(stmt)
        requests, total_withdrawn = [], 0
        for request in result.scalars().all():
            total_withdrawn += request.amount
            requests.append(WithdrawRequestDM(**request.__dict__))
        return requests, total_withdrawn

    async def get_one(self, **filters) -> WithdrawRequestDM | None:
        stmt = select(WithdrawRequest).filter_by(**filters)
        result = await self._session.execute(stmt)
        request = result.scalar_one_or_none()
        if request:
            return WithdrawRequestDM(**request.__dict__)
