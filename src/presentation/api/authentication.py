from fastapi import HTTPException, Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from src.application.interfaces.auth import TokenDecoder
from src.application.interfaces.user import UserReader
from src.domain.entities.user import UserDM
from src.infrastructure.gateways.errors import TokenError


async def get_user_by_token(
    request: Request, user_gateway: UserReader, token_gateway: TokenDecoder
) -> UserDM:
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(HTTP_401_UNAUTHORIZED)

    try:
        data = token_gateway.decode(token)
    except TokenError as e:
        raise HTTPException(HTTP_401_UNAUTHORIZED, str(e))

    try:
        user = await user_gateway.get_by_id(user_id=int(data["user_id"]))
    except ValueError:
        raise HTTPException(HTTP_401_UNAUTHORIZED)
    if not user:
        raise HTTPException(HTTP_400_BAD_REQUEST, "User does not exist")
    if user.is_banned:
        raise HTTPException(HTTP_403_FORBIDDEN, "User is banned")
    return user
