from pydantic import BaseModel


class InitDataDM(BaseModel):
    user: dict
    start_param: str | None
