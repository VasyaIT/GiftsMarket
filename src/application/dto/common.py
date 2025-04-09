from src.application.dto.base import BaseDTO


class ResponseDTO(BaseDTO):
    success: bool


class IdDTO(BaseDTO):
    id: int
