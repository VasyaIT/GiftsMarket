from sqlalchemy import insert, update
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

    async def set_completed(self, request_id: int) -> None:
        stmt = update(WithdrawRequest).filter_by(id=request_id).values(is_completed=True)
        await self._session.execute(stmt)
