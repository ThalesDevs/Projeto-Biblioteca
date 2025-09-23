import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ConfirmacaoEmail(Base):
    __tablename__ = "confirmacoes_email"
    __table_args__ = {"schema": "biblioteca"}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("biblioteca.usuarios.id"), nullable=False)

    token = Column(String(100), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    novo_email = Column(String(100), nullable=True)
    usado = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="confirmacoes_email")

    @classmethod
    def gerar_token(cls):
        return str(uuid.uuid4())

    @property
    def expirou(self):
        return datetime.utcnow() > self.expires_at
