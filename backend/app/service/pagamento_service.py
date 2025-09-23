
from sqlalchemy.orm import Session
from decimal import Decimal
from backend.app.domain.models.vendas.pedidos import Pedido
from backend.app.domain.models.vendas.pagamento import StatusPagamento
from backend.app.repositories.pagamento_repository import PagamentoRepository
from backend.app.utils.credit_card import luhn_check, mask_card, sanitize_card, validate_expiry, validate_cvv

class PagamentoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PagamentoRepository(db)

    def pagar_pedido_cartao(self, pedido_id: int, numero: str, validade: str, cvv: str, nome: str, bandeira: str | None = None):
        pedido = self.db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            raise ValueError("Pedido não encontrado.")
        if pedido.total <= 0:
            raise ValueError("Pedido sem itens ou valor inválido.")
        # Validações locais
        if not luhn_check(numero):
            raise ValueError("Número do cartão inválido.")
        if not validate_expiry(validade):
            raise ValueError("Validade do cartão inválida (MM/YY).")
        if not validate_cvv(cvv):
            raise ValueError("CVV inválido.")

        numero_s = sanitize_card(numero)
        mascara = mask_card(numero_s)

        # Criar registro de pagamento (pendente)
        pagamento = self.repo.criar_pagamento(pedido_id=pedido.id, valor=Decimal(pedido.total), bandeira=bandeira, cartao_final=mascara)

        # MOCK do gateway: aprova se último dígito é par; recusa se ímpar (apenas para testes)
        aprovado = int(numero_s[-1]) % 2 == 0
        if aprovado:
            self.repo.atualizar_status(pagamento.id, StatusPagamento.APROVADO, mensagem="Pagamento aprovado (mock).", gateway_id="MOCK-OK")
            # atualizar status do pedido, se o modelo aceitar string/Enum
            try:
                from app.domain.models.enums import StatusPedido
                pedido.status = StatusPedido.CONFIRMADO if hasattr(StatusPedido, "CONFIRMADO") else StatusPedido.PENDENTE
            except Exception:
                pass
            self.db.commit()
        else:
            self.repo.atualizar_status(pagamento.id, StatusPagamento.RECUSADO, mensagem="Cartão recusado (mock).", gateway_id="MOCK-FAIL")

        return pagamento
