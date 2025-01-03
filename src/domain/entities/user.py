from dataclasses import dataclass


@dataclass(slots=True)
class CreateUserDM:
    id: int
    username: str | None
    first_name: str | None


@dataclass(slots=True)
class UserDM:
    id: int
    username: str | None
    first_name: str | None
