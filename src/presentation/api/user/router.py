from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette import status

from src.application.dto.common import ResponseDTO
from src.application.dto.market import UpdateOrderDTO
from src.application.dto.user import LoginDTO, TokenDTO, UserDTO
from src.application.interactors import user
from src.application.interactors.errors import AlreadyExistError, NotAccessError, NotFoundError
from src.domain.entities.market import OrderDM, UserGiftDM


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post("/login")
@inject
async def user_login(dto: LoginDTO, interactor: FromDishka[user.LoginInteractor]) -> TokenDTO:
    try:
        token = await interactor(data=dto)
    except NotAccessError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Init data is not valid")
    return TokenDTO(token=token)


@user_router.get("/me")
@inject
async def get_current_user(interactor: FromDishka[user.GetUserInteractor]) -> UserDTO:
    """Get current user and referral link by token in cookies"""

    return await interactor()


@user_router.get("/gifts")
@inject
async def get_user_gifts(interactor: FromDishka[user.GetUserGiftsInteractor]) -> list[UserGiftDM]:
    return await interactor()


@user_router.get("/gifts/{id}")
@inject
async def get_user_gift(id: int, interactor: FromDishka[user.GetUserGiftInteractor]) -> UserGiftDM:
    try:
        return await interactor(id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@user_router.post("/gifts/{id}")
@inject
async def edit_gift(
    id: int, dto: UpdateOrderDTO, interactor: FromDishka[user.UpdateUserGiftInteractor]
) -> OrderDM:
    try:
        return await interactor(id, dto)
    except (NotFoundError, AlreadyExistError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@user_router.delete("/gifts/{id}")
@inject
async def delete_gift(id: int, interactor: FromDishka[user.DeleteUserGiftInteractor]) -> ResponseDTO:
    try:
        await interactor(id)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)
