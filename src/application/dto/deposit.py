from pydantic import BaseModel


class WalletAddressDTO(BaseModel):
    wallet_address: str
