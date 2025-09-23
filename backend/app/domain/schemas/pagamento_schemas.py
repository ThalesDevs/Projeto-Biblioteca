
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class PagamentoCartaoIn(BaseModel):
    numero: str = Field(..., min_length=12, max_length=19)
    nome: str = Field(..., min_length=2, max_length=80)
    validade: str = Field(..., description="MM/YY")
    cvv: str = Field(..., min_length=3, max_length=4)
    bandeira: Optional[str] = None

class PagamentoOut(BaseModel):
    id: int
    pedido_id: int
    valor: Decimal
    status: str
    cartao_final: str

    class Config:
        from_attributes = True
