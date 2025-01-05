from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException, Response
from starlette import status

from src.application.common.const import COOKIES_MAX_AGE
from src.application.dto.user import LoginDTO, UserDTO
from src.application.interactors.user import GetUserInteractor, LoginInteractor
from src.entrypoint.config import Config


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/me")
@inject
async def get_current_user(interactor: FromDishka[GetUserInteractor]) -> UserDTO:
    """Get current user and referral link by token in cookies"""

    return await interactor()


@user_router.post("/login")
@inject
async def user_login(
    dto: LoginDTO, interactor: FromDishka[LoginInteractor], config: FromDishka[Config]
) -> Response:
    token = await interactor(data=dto)
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Init data is not valid")
    response = Response()
    response.set_cookie(
        "token", token, httponly=True, secure=not config.app.DEBUG, samesite=None, max_age=COOKIES_MAX_AGE
    )
    return response
