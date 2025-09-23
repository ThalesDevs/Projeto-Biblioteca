from sqlalchemy.orm import Session
from app.repositories.pedido_repository import PedidoRepository
from app.domain.schemas.pedidos_schemas import ItemCarrinhoInput, PedidoOut

class PedidoService:
    def __init__(self, db: Session):
        self.repo = PedidoRepository(db)

    # -------------------- Carrinho --------------------
    def adicionar_ao_carrinho(self, usuario_id: int, item: ItemCarrinhoInput):
        return self.repo.adicionar_item_carrinho(usuario_id, item.livro_id, item.quantidade)

    def listar_carrinho(self, usuario_id: int):
        return self.repo.listar_itens_carrinho(usuario_id)

    def remover_do_carrinho(self, usuario_id: int, livro_id: int):
        return self.repo.remover_item_carrinho(usuario_id, livro_id)

    # -------------------- Pedido --------------------
    def finalizar_pedido(self, usuario_id: int) -> PedidoOut:
        itens_carrinho = self.repo.listar_itens_carrinho(usuario_id)
        if not itens_carrinho:
            raise Exception("Carrinho vazio")

        total = sum(item.quantidade * float(item.livro.preco) for item in itens_carrinho)
        pedido = self.repo.criar_pedido(usuario_id, total)

        for item in itens_carrinho:
            self.repo.adicionar_item_pedido(
                pedido.id,
                item.livro_id,
                item.quantidade,
                float(item.livro.preco)
            )
            self.repo.remover_item_carrinho(usuario_id, item.livro_id)

        return pedido

    def listar_pedidos_usuario(self, usuario_id: int, status: str = None, limite: int = 50):
        pedidos = self.repo.listar_pedidos_usuario(usuario_id)
        if status:
            pedidos = [p for p in pedidos if p.status.lower() == status.lower()]
        return pedidos[:limite]

    def listar_pedidos_por_usuario(self, usuario_id: int):
        """Alias compatível com router HTML"""
        return self.listar_pedidos_usuario(usuario_id)

    def obter_pedido(self, pedido_id: int, usuario_id: int):
        return self.repo.obter_pedido(pedido_id, usuario_id)

    def atualizar_status_pedido(self, pedido_id: int, usuario_id: int, novo_status: str):
        # Aqui você pode adicionar regras de validação de status
        return self.repo.atualizar_status_pedido(pedido_id, novo_status)

    # -------------------- Estatísticas --------------------
    def estatisticas_usuario(self, usuario_id: int):
        pedidos = self.repo.listar_pedidos_usuario(usuario_id)
        if not pedidos:
            return {
                "total_pedidos": 0,
                "valor_total_gasto": 0,
                "pedidos_por_status": {},
                "ticket_medio": 0
            }

        valores = [float(p.total) for p in pedidos]
        status_count = {}
        for p in pedidos:
            status_count[p.status] = status_count.get(p.status, 0) + 1

        return {
            "total_pedidos": len(pedidos),
            "valor_total_gasto": sum(valores),
            "pedidos_por_status": status_count,
            "ticket_medio": round(sum(valores) / len(valores), 2)
        }

    def pedidos_recentes(self, usuario_id: int, quantidade: int = 5):
        pedidos = self.repo.listar_pedidos_usuario(usuario_id)
        pedidos_ordenados = sorted(pedidos, key=lambda x: x.id, reverse=True)
        return pedidos_ordenados[:quantidade]
