# app/domain/models/vendas/item_carrinho.py
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

class ItemCarrinho(Base):
    __tablename__ = "itens_carrinho"
    __table_args__ = {"schema": "biblioteca"}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("biblioteca.usuarios.id"), nullable=False)
    livro_id = Column(Integer, ForeignKey("biblioteca.livros.id"), nullable=False)
    quantidade = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos corrigidos
    usuario = relationship("Usuario", back_populates="itens_carrinho")
    livro = relationship("Livro", back_populates="itens_carrinho")