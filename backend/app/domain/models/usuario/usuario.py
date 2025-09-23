from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from app.database import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "biblioteca"}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)

    email_confirmado = Column(Boolean, default=False)
    email_confirmado_em = Column(DateTime, nullable=True)

    cpf = Column(String(14), unique=True, nullable=True)
    telefone = Column(String(15), nullable=True)
    data_nascimento = Column(Date, nullable=True)
    ativo = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enderecos = relationship("EnderecoUsuario",
                             back_populates="usuario",
                             cascade="all, delete-orphan")

    cartoes_credito = relationship("CartaoCredito",
                                   back_populates="usuario",
                                   cascade="all, delete-orphan")

    pedidos = relationship("Pedido",
                           back_populates="usuario")

    itens_carrinho = relationship("ItemCarrinho",
                                  back_populates="usuario")

