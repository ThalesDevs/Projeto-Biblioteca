from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.dependencies import get_db
from app.utils.auth import get_current_user_dependency
from app.service.carrinho_service import CarrinhoService
from app.utils.templates_env import templates
from app.utils.template_utils import render_template_with_user
from app.domain.models.usuario.usuario import Usuario

router = APIRouter(tags=["Carrinho"])
logger = logging.getLogger("CarrinhoRouter")


class AtualizarQuantidadeRequest(BaseModel):
    quantidade: int


@router.get("/", response_class=HTMLResponse)
def pagina_carrinho(request: Request, db: Session = Depends(get_db),
                    user: Usuario = Depends(get_current_user_dependency)):
    try:
        service = CarrinhoService(db)
        # CORREÇÃO: usar user.id em vez de self.usuario_id
        itens = service.listar_itens(user.id)
        return render_template_with_user(templates, "carrinho.html", request, db, itens=itens)
    except Exception as e:
        logger.error(f"Erro ao carregar carrinho: {e}", exc_info=True)
        return templates.TemplateResponse(
            "erro.html", {"request": request, "mensagem": str(e)}, status_code=500
        )


@router.post("/adicionar")
def adicionar_item(livro_id: int = Form(...), quantidade: int = Form(...),
                   db: Session = Depends(get_db), user: Usuario = Depends(get_current_user_dependency)):
    try:
        service = CarrinhoService(db)
        service.adicionar(user.id, livro_id, quantidade)
        return RedirectResponse(url="/carrinho", status_code=status.HTTP_302_FOUND)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/remover/{livro_id}")
def remover_item(livro_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user_dependency)):
    try:
        service = CarrinhoService(db)
        service.remover(user.id, livro_id)
        return {"sucesso": True, "mensagem": "Item removido"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao remover item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/atualizar/{livro_id}")
def atualizar_quantidade(
        livro_id: int,
        payload: AtualizarQuantidadeRequest,  # CORREÇÃO: usar Pydantic model
        db: Session = Depends(get_db),
        user: Usuario = Depends(get_current_user_dependency)
):
    try:
        service = CarrinhoService(db)
        item_atualizado = service.atualizar_quantidade(user.id, livro_id, payload.quantidade)

        # Calcular novo preço do item
        preco_item = item_atualizado.livro.preco * payload.quantidade

        return {
            "sucesso": True,
            "mensagem": "Quantidade atualizada",
            "preco_item": f"R$ {preco_item:.2f}",
            "quantidade": payload.quantidade
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar quantidade: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# Endpoint opcional para limpar carrinho
@router.delete("/limpar")
def limpar_carrinho(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user_dependency)):
    try:
        service = CarrinhoService(db)
        itens_removidos = service.limpar_carrinho(user.id)
        return {"sucesso": True, "mensagem": f"{itens_removidos} itens removidos do carrinho"}
    except Exception as e:
        logger.error(f"Erro ao limpar carrinho: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno do servidor")