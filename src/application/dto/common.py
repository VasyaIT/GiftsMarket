from src.application.common.const import GiftType
from src.application.dto.base import BaseDTO


class ResponseDTO(BaseDTO):
    success: bool


class GiftImagesDTO(BaseDTO):
    data: dict[GiftType, list[str]]
