from dataclasses import dataclass


@dataclass(slots=True)
class InitDataDM:
    user: dict
    start_param: str | None
