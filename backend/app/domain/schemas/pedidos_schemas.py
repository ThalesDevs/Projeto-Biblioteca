from pydantic import BaseModel
from typing import List

class ItemCarrinhoInput(BaseModel):
    livro_id: int
    quantidade: int

class ItemPedidoOut(BaseModel):
    id: int
    livro_id: int
    quantidade: int
    preco_unitario: float

    class Config:
        from_attributes = True

class PedidoOut(BaseModel):
    id: int
    total: float
    status: str
    itens: List[ItemPedidoOut] = []

    class Config:
        from_attributes = True