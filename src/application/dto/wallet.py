from pydantic import BaseModel, Field


class WalletAddressDTO(BaseModel):
    wallet_address: str = Field(examples=["UQBB7mTV0zUR7OlzoJKLjbTk5c13rngbgpNln3zJVncbuMhb"])


class WithdrawRequestDTO(BaseModel):
    amount: float = Field(ge=0)
    wallet: str = Field(
        min_length=40, max_length=60, examples=["UQBB7mTV0zUR7OlzoJKLjbTk5c13rngbgpNln3zJVncbuMhb"]
    )
