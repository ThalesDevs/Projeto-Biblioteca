
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.dependencies import get_db
from backend.app.utils.auth import get_current_user_dependency
from backend.app.service.pagamento_service import PagamentoService
from backend.app.domain.schemas.pagamento_schemas import PagamentoCartaoIn, PagamentoOut
from backend.app.domain.models.usuario.usuario import Usuario

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.post("/pedido/{pedido_id}/cartao", response_model=PagamentoOut, status_code=status.HTTP_201_CREATED)
def pagar_pedido_cartao(pedido_id: int, payload: PagamentoCartaoIn, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user_dependency())):
    try:
        pg = PagamentoService(db).pagar_pedido_cartao(
            pedido_id=pedido_id,
            numero=payload.numero,
            validade=payload.validade,
            cvv=payload.cvv,
            nome=payload.nome,
            bandeira=payload.bandeira
        )
        return pg
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao processar pagamento.")


@router.post("/lote", status_code=status.HTTP_200_OK)
def pagar_varios_pedidos(pedido_ids: list[int], payload: PagamentoCartaoIn, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user_dependency())):
    try:
        service = PagamentoService(db)
        resultados = []
        for pid in pedido_ids:
            pg = service.pagar_pedido_cartao(pid, payload.numero, payload.validade, payload.cvv, payload.nome, payload.bandeira)
            resultados.append({"pedido_id": pid, "status": pg.status.value})
        return {"resultados": resultados}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao processar pagamento em lote.")
