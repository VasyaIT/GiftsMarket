from pydantic import BaseModel


class BotInfoDM(BaseModel):
    id: int
    first_name: str
    username: str
