from pydantic import BaseModel


class CreateWithdrawRequestDM(BaseModel):
    user_id: int
    amount: float
    wallet: str


class WithdrawRequestDM(CreateWithdrawRequestDM):
    id: int
