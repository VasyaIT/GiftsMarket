from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from src.application.dto.deposit import WalletAddressDTO
from src.entrypoint.config import Config


deposit_router = APIRouter(tags=["Deposit"])


@deposit_router.get("/deposit-wallet-address")
@inject
async def get_deposit_wallet_address(config: FromDishka[Config]) -> WalletAddressDTO:
    return WalletAddressDTO(wallet_address=config.tonapi.DEPOSIT_ADDRESS)
