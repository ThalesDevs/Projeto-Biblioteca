from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import logging

from app.dependencies import get_db
from app.domain.schemas.pedidos_schemas import ItemPedidoOut, ItemCarrinhoInput
from app.utils.auth import get_current_user_dependency
from app.service.carrinho_service import CarrinhoService
from app.utils.templates_env import templates
from app.utils.template_utils import render_template_with_user


router = APIRouter(tags=["Carrinho"])
logger = logging.getLogger("CarrinhoRouter")


@router.get("/", response_class=HTMLResponse)
def pagina_carrinho(
        request: Request,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user_dependency)
):
    if not user:
        return RedirectResponse(url="/auth/login")

    service = CarrinhoService(db)
    itens = service.listar_itens(user["id"])

    itens_out = [
        ItemPedidoOut(
            id=item.id,
            livro_id=item.livro_id,
            quantidade=item.quantidade,
            preco_unitario=service.calcular_preco_item(item)
        )
        for item in itens
    ]

    return render_template_with_user(
        templates,
        "carrinho.html",
        request,
        db,
        itens=itens_out,
        usuario=user
    )


@router.post("/adicionar")
def adicionar_item(
        payload: ItemCarrinhoInput,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user_dependency)
):
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    service = CarrinhoService(db)
    service.adicionar(user["id"], payload.livro_id, payload.quantidade)
    return RedirectResponse(url="/carrinho", status_code=302)


@router.delete("/remover/{livro_id}")
def remover_item(
        livro_id: int,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user_dependency)
):
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    service = CarrinhoService(db)
    service.remover(user["id"], livro_id)
    return {"sucesso": True, "mensagem": "Item removido"}


@router.put("/atualizar/{livro_id}")
def atualizar_quantidade(
        livro_id: int,
        payload: ItemCarrinhoInput,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user_dependency)
):
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    service = CarrinhoService(db)
    item_atualizado = service.atualizar_quantidade(user["id"], livro_id, payload.quantidade)
    preco_item = service.calcular_preco_item(item_atualizado)

    return {
        "sucesso": True,
        "mensagem": "Quantidade atualizada",
        "preco_item": f"R$ {preco_item:.2f}",
        "quantidade": payload.quantidade
    }


@router.delete("/limpar")
def limpar_carrinho(
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user_dependency)
):
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    service = CarrinhoService(db)
    itens_removidos = service.limpar_carrinho(user["id"])
    return {"sucesso": True, "mensagem": f"{itens_removidos} itens removidos do carrinho"}
