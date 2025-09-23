from sqlalchemy.orm import relationship
try:
    from backend.app.domain.models.vendas.pedidos import Pedido
    Pedido.pagamento = relationship("Pagamento", back_populates="pedido", uselist=False, cascade="all, delete-orphan")
except Exception:
    pass
