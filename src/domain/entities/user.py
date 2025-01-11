from datetime import datetime

from pydantic import BaseModel

from src.domain.entities.market import OrderDM
from src.domain.entities.wallet import WithdrawRequestDM


class CreateUserDM(BaseModel):
    id: int
    username: str | None
    first_name: str | None
    deposit_comment: str


class UserDM(BaseModel):
    id: int
    username: str | None
    first_name: str | None
    deposit_comment: str
    balance: float
    commission: float
    is_banned: bool = False
    created_at: datetime


class UpdateUserBalanceDM(BaseModel):
    id: int | None = None
    deposit_comment: str | None = None
    amount: float


class FullUserInfoDM(UserDM):
    orders: list[OrderDM]
    withdraw_requests: list[WithdrawRequestDM]
    total_withdrawn: float
