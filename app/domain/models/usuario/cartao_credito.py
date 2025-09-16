from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CartaoCredito(Base):
    __tablename__ = "cartoes_credito"
    __table_args__ = {"schema": "biblioteca"}  # ajuste se for outro schema

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("biblioteca.usuarios.id", ondelete="CASCADE"), nullable=False)

    numero = Column(String(20), nullable=False)
    nome_titular = Column(String(255), nullable=False)
    validade = Column(String(7), nullable=False)  # formato MM/AAAA
    cvv = Column(String(4), nullable=False)

    usuario = relationship("Usuario", back_populates="cartoes_credito")
