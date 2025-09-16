from sqlalchemy.orm import Session
from app.repositories.carrinho_repository import CarrinhoRepository

class CarrinhoService:
    def __init__(self, db: Session):
        self.repo = CarrinhoRepository(db)

    def adicionar(self, usuario_id: int, livro_id: int, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero")
        return self.repo.adicionar_item(usuario_id, livro_id, quantidade)

    def listar_itens(self, usuario_id: int):
        return self.repo.listar_itens(usuario_id)

    def remover(self, usuario_id: int, livro_id: int):
        item = self.repo.remover_item(usuario_id, livro_id)
        if not item:
            raise ValueError("Item não encontrado")
        return item

    def atualizar_quantidade(self, usuario_id: int, livro_id: int, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero")
        item = self.repo.atualizar_quantidade_item(usuario_id, livro_id, quantidade)
        if not item:
            raise ValueError("Item não encontrado")
        return item

    def limpar_carrinho(self, usuario_id: int):
        return self.repo.limpar_carrinho(usuario_id)

    def calcular_preco_item(self, item):
        return item.livro.preco * item.quantidade
