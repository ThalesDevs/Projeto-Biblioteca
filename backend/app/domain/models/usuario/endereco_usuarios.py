# app/domain/models/usuario/endereco_usuario.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class EnderecoUsuario(Base):
    __tablename__ = "endereco_usuarios"
    __table_args__ = {"schema": "biblioteca"}  # ajuste se usar schema diferente

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("biblioteca.usuarios.id", ondelete="CASCADE"), nullable=False)
    rua = Column(String(255), nullable=False)
    numero = Column(String(50), nullable=True)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    cep = Column(String(20), nullable=False)

    # relacionamento reverso
    usuario = relationship("Usuario", back_populates="enderecos")
