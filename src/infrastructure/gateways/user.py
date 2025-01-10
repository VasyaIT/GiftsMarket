from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.user import UserReader, UserSaver
from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM
from src.infrastructure.models.user import User, UserReferral


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

    async def update_user(self, data: dict, **filters) -> UserDM | None:
        stmt = update(User).values(data).filter_by(**filters).returning(User)
        result = await self._session.execute(stmt)
        new_user = result.scalar_one_or_none()
        if new_user:
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

    async def add_referral(self, referrer_id: int, referral: UserDM) -> bool:
        stmt = (
            insert(UserReferral)
            .values(referrer_id=referrer_id, referral_id=referral.id)
            .returning(UserReferral)
        )
        try:
            result = await self._session.execute(stmt)
        except IntegrityError:
            return False

        return not result.scalar_one().referrer.is_banned

    async def update_referrer_balance(self, referrer_id: int, amount: float) -> None:
        stmt = (
            update(User)
            .values(balance=User.balance + amount, commission=User.commission + amount)
            .filter_by(id=referrer_id)
        )
        await self._session.execute(stmt)

    async def get_referrer(self, user_id: int) -> UserDM | None:
        stmt = select(UserReferral).filter_by(referral_id=user_id)
        result = await self._session.execute(stmt)
        user_referral = result.scalar_one_or_none()
        return UserDM(**user_referral.referrer.__dict__) if user_referral else None

    async def get_count_referrals(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(UserReferral).filter_by(referrer_id=user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_count_users(self) -> int:
        stmt = select(func.count()).select_from(User)
        result = await self._session.execute(stmt)
        return result.scalar_one()
