
from sqlalchemy.orm import Session
from backend.app.domain.models.vendas.pagamento import Pagamento, StatusPagamento

class PagamentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar_pagamento(self, pedido_id: int, valor, bandeira: str | None, cartao_final: str) -> Pagamento:
        pg = Pagamento(pedido_id=pedido_id, valor=valor, bandeira=bandeira, cartao_final=cartao_final)
        self.db.add(pg)
        self.db.commit()
        self.db.refresh(pg)
        return pg

    def atualizar_status(self, pagamento_id: int, status: StatusPagamento, mensagem: str | None = None, gateway_id: str | None = None) -> Pagamento | None:
        pg = self.db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
        if not pg:
            return None
        pg.status = status
        if mensagem is not None:
            pg.mensagem = mensagem
        if gateway_id is not None:
            pg.gateway_id = gateway_id
        self.db.commit()
        self.db.refresh(pg)
        return pg
