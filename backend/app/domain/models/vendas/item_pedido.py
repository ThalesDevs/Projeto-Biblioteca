# app/domain/models/vendas/item_pedido.py
from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    __table_args__ = {"schema": "biblioteca"}

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("biblioteca.pedidos.id"), nullable=False)
    livro_id = Column(Integer, ForeignKey("biblioteca.livros.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens")
    livro = relationship("Livro", back_populates="itens_pedido")

    @property
    def subtotal(self):
        """Calcula o subtotal do item (quantidade * preço unitário)"""
        return float(self.quantidade * self.preco_unitario)