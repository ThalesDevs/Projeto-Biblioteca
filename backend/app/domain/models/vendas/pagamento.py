
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from backend.app.database import Base
from enum import Enum as PyEnum

class StatusPagamento(str, PyEnum):
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"
    FALHA = "FALHA"

class Pagamento(Base):
    __tablename__ = "pagamentos"
    __table_args__ = {"schema": "biblioteca"}

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("biblioteca.pedidos.id"), nullable=False, index=True)
    valor = Column(Numeric(10,2), nullable=False)
    bandeira = Column(String(20), nullable=True)
    cartao_final = Column(String(20), nullable=True)  # somente ****1234
    status = Column(Enum(StatusPagamento), default=StatusPagamento.PENDENTE, index=True)
    gateway_id = Column(String(100), nullable=True)
    mensagem = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pedido = relationship("Pedido", back_populates="pagamento", uselist=False)
