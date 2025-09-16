
# This module establishes the relationship on Pedido if available at import time.
# Import this alongside pedidos model in app startup to ensure relationship exists.
from sqlalchemy.orm import relationship
try:
    from app.domain.models.vendas.pedidos import Pedido
    Pedido.pagamento = relationship("Pagamento", back_populates="pedido", uselist=False, cascade="all, delete-orphan")
except Exception:
    # If Pedido import fails during some import order, ignore silently.
    pass
