from pydantic import BaseModel


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


class UpdateUserBalanceDM(BaseModel):
    id: int | None = None
    deposit_comment: str | None = None
    amount: float
