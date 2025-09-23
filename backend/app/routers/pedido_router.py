from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from backend.app.dependencies import get_db
from backend.app.utils.template_utils import get_current_user_dependency, render_template_with_user
from backend.app.service.pedido_service import PedidoService
from backend.app.domain.schemas.pedidos_schemas import ItemCarrinhoInput, PedidoOut

logger = logging.getLogger("PedidoRouter")
router = APIRouter(tags=["Pedidos"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, response_model=None)
def pagina_pedidos(
        request: Request,
        user_data: Optional[dict] = Depends(get_current_user_dependency)
):
    """Página HTML de pedidos"""
    try:
        if not user_data:
            return RedirectResponse(url="/auth/login", status_code=302)

        # Obter db manualmente para este endpoint
        from app.dependencies import get_db
        db = next(get_db())
        try:
            service = PedidoService(db)
            pedidos = service.listar_pedidos_por_usuario(user_data["id"])

            return render_template_with_user(
                templates,
                "pedido.html",
                request,
                db,
                pedidos=pedidos
            )
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Erro ao carregar página de pedidos: {e}", exc_info=True)
        return templates.TemplateResponse(
            "erro.html",
            {"request": request, "mensagem": "Erro ao carregar pedidos"},
            status_code=500
        )


@router.get("/listar", response_model=List[PedidoOut])
def listar_pedidos_usuario(
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency),  # ✅ CORREÇÃO
        status_pedido: Optional[str] = Query(None, description="Filtrar por status"),
        limite: int = Query(50, ge=1, le=200, description="Limite de resultados")
):
    """Listar histórico de pedidos do usuário"""
    try:
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        service = PedidoService(db)
        pedidos = service.listar_pedidos_usuario(user_data["id"])  # ✅ CORREÇÃO

        if status_pedido:
            pedidos = [p for p in pedidos if p.status.lower() == status_pedido.lower()]

        pedidos = pedidos[:limite]
        logger.info(f"Listados {len(pedidos)} pedidos para usuário {user_data['id']}")

        return pedidos
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar pedidos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/{pedido_id}", response_model=PedidoOut)
def obter_pedido(
        pedido_id: int,
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)  # ✅ CORREÇÃO
):
    """Obter detalhes de um pedido específico"""
    try:
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        service = PedidoService(db)
        pedido = service.obter_pedido(pedido_id, user_data["id"])  # ✅ CORREÇÃO

        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido {pedido_id} não encontrado"
            )

        logger.info(f"Pedido {pedido_id} acessado por usuário {user_data['id']}")
        return pedido
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter pedido {pedido_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.post("/finalizar", response_model=None)
async def finalizar_pedido(
        request: Request,
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)  # ✅ CORREÇÃO
):
    """Finalizar pedido com todos os itens do carrinho"""
    try:
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        service = PedidoService(db)
        pedido = service.finalizar_pedido(user_data["id"])  # ✅ CORREÇÃO

        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Carrinho vazio ou erro ao finalizar pedido"
            )

        logger.info(f"Pedido {pedido.id} finalizado para usuário {user_data['id']}")

        accept_header = request.headers.get("accept", "")
        content_type = request.headers.get("content-type", "")

        if "text/html" in accept_header or "application/x-www-form-urlencoded" in content_type:
            return RedirectResponse(url="/pedidos/", status_code=302)

        return pedido

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao finalizar pedido: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.put("/{pedido_id}/status", response_model=None)
def atualizar_status_pedido(
        pedido_id: int,
        novo_status: str,
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)  # ✅ CORREÇÃO
):
    """Atualizar status do pedido"""
    try:
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        status_permitidos = ["cancelado"]

        if novo_status.lower() not in status_permitidos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status '{novo_status}' não pode ser alterado pelo usuário"
            )

        service = PedidoService(db)

        pedido = service.obter_pedido(pedido_id, user_data["id"])  # ✅ CORREÇÃO
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )

        if novo_status.lower() == "cancelado" and pedido.status.lower() in ["entregue", "cancelado"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido não pode ser cancelado neste status"
            )

        pedido_atualizado = service.atualizar_status_pedido(pedido_id, novo_status)

        logger.info(f"Status do pedido {pedido_id} atualizado para '{novo_status}' por usuário {user_data['id']}")

        return {
            "sucesso": True,
            "mensagem": f"Status do pedido atualizado para '{novo_status}'",
            "pedido": pedido_atualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar status do pedido {pedido_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/estatisticas/usuario")
def estatisticas_pedidos_usuario(
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)  # ✅ CORREÇÃO
):
    """Estatísticas dos pedidos do usuário"""
    try:
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        service = PedidoService(db)
        pedidos = service.listar_pedidos_usuario(user_data["id"])  # ✅ CORREÇÃO

        if not pedidos:
            return {
                "total_pedidos": 0,
                "valor_total_gasto": 0,
                "pedidos_por_status": {},
                "ticket_medio": 0
            }

        valores = [float(p.total) for p in pedidos]
        status_count = {}

        for pedido in pedidos:
            status_count[pedido.status] = status_count.get(pedido.status, 0) + 1

        stats = {
            "total_pedidos": len(pedidos),
            "valor_total_gasto": sum(valores),
            "pedidos_por_status": status_count,
            "ticket_medio": round(sum(valores) / len(valores), 2) if valores else 0
        }

        logger.info(f"Estatísticas calculadas para usuário {user_data['id']}: {stats}")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/recentes/{quantidade}")
def pedidos_recentes(
        quantidade: int,
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)  # ✅ CORREÇÃO
):
    """Obter pedidos mais recentes do usuário"""
    try:
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        if quantidade <= 0 or quantidade > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantidade deve ser entre 1 e 50"
            )

        service = PedidoService(db)
        pedidos = service.listar_pedidos_usuario(user_data["id"])  # ✅ CORREÇÃO

        pedidos_recentes = sorted(
            pedidos,
            key=lambda x: x.id,
            reverse=True
        )[:quantidade]

        logger.info(f"Retornados {len(pedidos_recentes)} pedidos recentes para usuário {user_data['id']}")

        return {
            "pedidos_recentes": pedidos_recentes,
            "total_retornados": len(pedidos_recentes)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter pedidos recentes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/status")
def status_pedidos():
    """Status do serviço de pedidos"""
    return {
        "status": "online",
        "service": "PedidoRouter",
        "endpoints": [
            "/ - GET (página HTML)",
            "/listar - GET (listar pedidos)",
            "/{pedido_id} - GET (obter pedido)",
            "/finalizar - POST",
            "/{pedido_id}/status - PUT (atualizar status)",
            "/estatisticas/usuario - GET",
            "/recentes/{quantidade} - GET",
            "/status - GET"
        ]
    }