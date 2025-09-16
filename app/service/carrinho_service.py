from sqlalchemy.orm import Session
from app.repositories.carrinho_repository import CarrinhoRepository
from app.domain.models.vendas.item_carrinho import ItemCarrinho

class CarrinhoService:
    def __init__(self, db: Session):
        self.repo = CarrinhoRepository(db)

    def adicionar(self, usuario_id: int, livro_id: int, quantidade: int):
        # Regras de negócio
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero")

        # Aqui você pode adicionar validação de livro existente, estoque, etc.
        item = self.repo.adicionar_item(usuario_id, livro_id, quantidade)
        return item

    def listar(self, usuario_id: int):
        return self.repo.listar_itens(usuario_id)

    def listar_itens(self, usuario_id: int):
        """Alias para compatibilidade com router"""
        return self.listar(usuario_id)

    def remover(self, usuario_id: int, livro_id: int):
        item = self.repo.remover_item(usuario_id, livro_id)
        if not item:
            raise ValueError("Item não encontrado no carrinho")
        return item

    def atualizar_quantidade(self, usuario_id: int, livro_id: int, nova_quantidade: int):
        if nova_quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero")
        item = self.repo.atualizar_quantidade(usuario_id, livro_id, nova_quantidade)
        if not item:
            raise ValueError("Item não encontrado no carrinho")
        return item

    def limpar_carrinho(self, usuario_id: int):
        return self.repo.limpar_carrinho(usuario_id)
