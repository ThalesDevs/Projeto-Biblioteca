from sqlalchemy.orm import Session
from backend.app.domain.models.vendas.pedidos import Pedido
from backend.app.domain.models.vendas.item_carrinho import ItemCarrinho
from backend.app.domain.models.vendas.item_pedido import ItemPedido

class PedidoRepository:
    def __init__(self, db: Session):
        self.db = db

    # Itens do carrinho
    def listar_itens_carrinho(self, usuario_id: int):
        return self.db.query(ItemCarrinho).filter(ItemCarrinho.usuario_id == usuario_id).all()

    def adicionar_item_carrinho(self, usuario_id: int, livro_id: int, quantidade: int):
        item = (
            self.db.query(ItemCarrinho)
            .filter(ItemCarrinho.usuario_id == usuario_id, ItemCarrinho.livro_id == livro_id)
            .first()
        )
        if item:
            item.quantidade += quantidade
        else:
            item = ItemCarrinho(usuario_id=usuario_id, livro_id=livro_id, quantidade=quantidade)
            self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remover_item_carrinho(self, usuario_id: int, livro_id: int):
        item = (
            self.db.query(ItemCarrinho)
            .filter(ItemCarrinho.usuario_id == usuario_id, ItemCarrinho.livro_id == livro_id)
            .first()
        )
        if item:
            self.db.delete(item)
            self.db.commit()
        return item

    # Pedidos
    def criar_pedido(self, usuario_id: int, total: float):
        pedido = Pedido(usuario_id=usuario_id, status="PENDENTE")
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    def adicionar_item_pedido(self, pedido_id: int, livro_id: int, quantidade: int, preco_unitario: float):
        item = ItemPedido(
            pedido_id=pedido_id,
            livro_id=livro_id,
            quantidade=quantidade,
            preco_unitario=preco_unitario
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def listar_pedidos_usuario(self, usuario_id: int):
        return self.db.query(Pedido).filter(Pedido.usuario_id == usuario_id).all()

    def obter_pedido(self, pedido_id: int, usuario_id: int):
        return self.db.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.usuario_id == usuario_id
        ).first()

    def atualizar_status_pedido(self, pedido_id: int, novo_status: str):
        pedido = self.db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if pedido:
            pedido.status = novo_status
            self.db.commit()
            self.db.refresh(pedido)
        return pedido