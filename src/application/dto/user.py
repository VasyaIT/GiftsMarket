from src.application.dto.base import BaseDTO


class TokenDTO(BaseDTO):
    token: str


class UserDTO(BaseDTO):
    id: int
    username: str | None
    first_name: str | None
    balance: float
    commission: float
    deposit_comment: str
    referral_link: str
    count_referrals: int


class LoginDTO(BaseDTO):
    init_data: str
