# app/domain/models/vendas/pedidos.py
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.domain.models.enums import StatusPedido

class Pedido(Base):
    __tablename__ = "pedidos"
    __table_args__ = {"schema": "biblioteca"}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("biblioteca.usuarios.id"), nullable=False)
    status = Column(Enum(StatusPedido), default=StatusPedido.PENDENTE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

    @property
    def total(self):
        """Calcula o total do pedido baseado nos itens"""
        return sum(item.subtotal for item in self.itens)

    @property
    def total_itens(self):
        """Retorna o número total de itens no pedido"""
        return sum(item.quantidade for item in self.itens)
