from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException, Response
from starlette import status

from src.application.common.const import COOKIES_MAX_AGE
from src.application.dto.user import LoginDTO, UserDTO
from src.application.interactors.user import LoginInteractor


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post("/login")
@inject
async def user_login(dto: LoginDTO, interactor: FromDishka[LoginInteractor]) -> Response:
    token = await interactor(data=dto)
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Init data is not valid")
    response = Response()
    response.set_cookie("token", token, httponly=True, secure=True, samesite=None, max_age=COOKIES_MAX_AGE)
    return response
