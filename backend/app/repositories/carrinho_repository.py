from sqlalchemy.orm import Session
from backend.app.domain.models.vendas.item_carrinho import ItemCarrinho

class CarrinhoRepository:
    def __init__(self, db: Session):
        self.db = db

    def adicionar_item(self, usuario_id: int, livro_id: int, quantidade: int):
        item = self.db.query(ItemCarrinho).filter_by(usuario_id=usuario_id, livro_id=livro_id).first()
        if item:
            item.quantidade += quantidade
        else:
            item = ItemCarrinho(usuario_id=usuario_id, livro_id=livro_id, quantidade=quantidade)
            self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def listar_itens(self, usuario_id: int):
        return self.db.query(ItemCarrinho).filter_by(usuario_id=usuario_id).all()

    def remover_item(self, usuario_id: int, livro_id: int):
        item = self.db.query(ItemCarrinho).filter_by(usuario_id=usuario_id, livro_id=livro_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()
        return item

    def atualizar_quantidade(self, usuario_id: int, livro_id: int, nova_quantidade: int):
        item = self.db.query(ItemCarrinho).filter_by(usuario_id=usuario_id, livro_id=livro_id).first()
        if item:
            item.quantidade = nova_quantidade
            self.db.commit()
            self.db.refresh(item)
        return item

    def limpar_carrinho(self, usuario_id: int):
        itens = self.db.query(ItemCarrinho).filter_by(usuario_id=usuario_id).all()
        for item in itens:
            self.db.delete(item)
        self.db.commit()
        return len(itens)
