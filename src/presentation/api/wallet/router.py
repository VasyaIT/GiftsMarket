from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.application.dto.common import ResponseDTO
from src.application.dto.wallet import WalletAddressDTO, WithdrawRequestDTO
from src.application.interactors.errors import NotAccessError, NotEnoughBalanceError
from src.application.interactors.wallet import WithdrawRequestInteractor
from src.entrypoint.config import Config


wallet_router = APIRouter(tags=["Wallet"])


@wallet_router.get("/deposit-wallet-address")
@inject
async def get_deposit_wallet_address(config: FromDishka[Config]) -> WalletAddressDTO:
    return WalletAddressDTO(wallet_address=config.tonapi.DEPOSIT_ADDRESS)


@wallet_router.post("/create-withdraw-request")
@inject
async def create_withdraw_request(
    dto: WithdrawRequestDTO, interactor: FromDishka[WithdrawRequestInteractor]
) -> ResponseDTO:
    try:
        await interactor(dto)
    except (NotEnoughBalanceError, NotAccessError) as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)
