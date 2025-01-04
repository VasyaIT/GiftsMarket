from src.application.dto.base import BaseDTO


class UserDTO(BaseDTO):
    id: int
    username: str | None
    first_name: str | None
    balance: float = 0
    deposit_comment: str


class LoginDTO(BaseDTO):
    init_data: str
