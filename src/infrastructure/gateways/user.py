from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.user import UserReader, UserSaver
from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM
from src.infrastructure.models.user import User


class UserGateway(UserReader, UserSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> UserDM | None:
        stmt = select(User).filter_by(id=user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def save(self, user: CreateUserDM) -> UserDM:
        stmt = insert(User).values(user.model_dump()).returning(User)
        result = await self._session.execute(stmt)
        new_user = result.scalar_one()
        return UserDM(**new_user.__dict__)

    async def get_by_comment(self, comment: str) -> UserDM | None:
        stmt = select(User).filter_by(deposit_comment=comment)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def update_balance(self, data: UpdateUserBalanceDM) -> UserDM | None:
        filter_by = {"deposit_comment": data.deposit_comment}
        if data.id:
            filter_by = {"id": data.id}
        stmt = (
            update(User)
            .filter_by(**filter_by)
            .values(balance=User.balance + data.amount)
            .returning(User)
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)
