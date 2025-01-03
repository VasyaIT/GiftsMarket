from dataclasses import asdict

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import CreateUserDM, UserDM
from src.infrastructure.models.user import User


class UserGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> UserDM | None:
        stmt = select(User).filter_by(id=user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def save(self, user: CreateUserDM) -> UserDM:
        stmt = insert(User).values(asdict(user)).returning(User)
        result = await self._session.execute(stmt)
        new_user = result.scalar_one()
        return UserDM(**new_user.__dict__)
