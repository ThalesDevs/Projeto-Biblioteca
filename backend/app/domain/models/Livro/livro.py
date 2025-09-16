from pydantic.v1 import BaseModel
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    ano = Column(Integer, nullable=True)
    preco = Column(Numeric, nullable=True)
    estoque = Column(Integer, nullable=True)
    capa_url = Column(String, nullable=True)
    data_criacao = Column(DateTime, nullable=True)
    data_atualizacao = Column(DateTime, nullable=True)
    isbn = Column(String, nullable=True)
    slug = Column(String, nullable=True)

    # Relacionamentos corrigidos
    itens_carrinho = relationship("ItemCarrinho", back_populates="livro")
    itens_pedido = relationship("ItemPedido", back_populates="livro")

    @property
    def preco_formatado(self):
        """Retorna o preço formatado como moeda brasileira"""
        if self.preco is None:
            return "R$ 0,00"
        return f"R$ {float(self.preco):.2f}".replace(".", ",")

    def __repr__(self):
        return f"<Livro(titulo='{self.titulo}', autor='{self.autor}')>"


