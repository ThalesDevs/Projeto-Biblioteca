from fastapi import APIRouter, Depends, Request, Form, Query, status, HTTPException, Path
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.dependencies import get_db
from app.domain.schemas.cria_livro import LivroCreate, LivroOut, LivroUpdate
from app.service.livro_service import LivroService
from app.utils.template_utils import render_template_with_user, get_current_user_dependency

logger = logging.getLogger("LivroRouter")
router = APIRouter(tags=["Livros"])

# ---------------------- Templates ----------------------
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


# ---------------------- PÁGINA HTML ----------------------
@router.get("/", response_class=HTMLResponse, response_model=None)
def pagina_livros(request: Request, db: Session = Depends(get_db)):
    """Página principal de livros"""
    try:
        service = LivroService(db)
        livros = service.listar_livros()
        return render_template_with_user(templates, "livro.html", request, db, livros=livros)
    except Exception as e:
        logger.error(f"Erro ao carregar página de livros: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ---------------------- CRUD ----------------------
@router.get("/listar", response_model=List[LivroOut])
def listar_livros(
        db: Session = Depends(get_db),
        autor: Optional[str] = Query(None, description="Filtrar por autor"),
        titulo: Optional[str] = Query(None, description="Filtrar por título"),
        ano: Optional[int] = Query(None, description="Filtrar por ano"),
        preco_min: Optional[float] = Query(None, description="Preço mínimo"),
        preco_max: Optional[float] = Query(None, description="Preço máximo"),
        estoque_min: Optional[int] = Query(None, description="Estoque mínimo"),
        estoque_max: Optional[int] = Query(None, description="Estoque máximo"),
        skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
        limite: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Lista livros com filtros opcionais"""
    try:
        service = LivroService(db)
        livros = service.listar_livros(
            autor=autor,
            titulo=titulo,
            ano=ano,
            preco_min=preco_min,
            preco_max=preco_max,
            estoque_min=estoque_min,
            estoque_max=estoque_max,
            skip=skip,
            limite=limite
        )
        return livros
    except Exception as e:
        logger.error(f"Erro ao listar livros: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar livros")


@router.get("/{livro_id}", response_model=LivroOut)
def obter_livro(
        livro_id: int = Path(..., description="ID do livro", gt=0),
        db: Session = Depends(get_db)
):
    """Obtém um livro específico por ID - CORRIGIDO"""
    try:
        service = LivroService(db)
        livro = service.obter_livro(livro_id)
        return livro
    except HTTPException:
        # Re-raise HTTPExceptions do service
        raise
    except Exception as e:
        logger.error(f"Erro ao obter livro {livro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/slug/{slug}", response_model=LivroOut)
def obter_livro_por_slug(
        slug: str = Path(..., description="Slug do livro"),
        db: Session = Depends(get_db)
):
    """Obtém um livro específico por slug"""
    try:
        service = LivroService(db)
        livro = service.obter_livro_por_slug(slug)
        return livro
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter livro por slug {slug}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/", response_model=LivroOut, status_code=status.HTTP_201_CREATED)
def criar_livro(
        livro: LivroCreate,
        db: Session = Depends(get_db),
     #   user_data: Optional[dict] = Depends(get_current_user_dependency)
):
    """Cria um novo livro"""
    # Verificar autenticação
 #   if not user_data:
   #     raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        service = LivroService(db)
        livro_criado = service.adicionar_livro(livro)
        logger.info(f"Livro criado com sucesso: ID {livro_criado.id}")
        return livro_criado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar livro: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar livro")


@router.patch("/{livro_id}", response_model=LivroOut)
def atualizar_livro(
        livro_id: int = Path(..., description="ID do livro", gt=0),
        dados_atualizacao: LivroUpdate = ...,
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)
):
    """Atualiza um livro existente - CORRIGIDO"""
    # Verificar autenticação
    if not user_data:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        service = LivroService(db)
        livro_atualizado = service.atualizar_livro(livro_id, dados_atualizacao)
        logger.info(f"Livro {livro_id} atualizado com sucesso")
        return livro_atualizado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar livro {livro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar livro")


@router.delete("/{livro_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_livro(
        livro_id: int = Path(..., description="ID do livro", gt=0),
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)
):
    """Deleta um livro - CORRIGIDO"""
    # Verificar autenticação
    if not user_data:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        service = LivroService(db)
        sucesso = service.deletar_livro(livro_id)

        if sucesso:
            logger.info(f"Livro {livro_id} deletado com sucesso")
            return  # Retorna 204 No Content
        else:
            raise HTTPException(status_code=500, detail="Falha ao deletar o livro")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar livro {livro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar livro")


# ---------------------- BUSCAS ----------------------
@router.get("/buscar/filtros")
def buscar_livros_com_filtros(
        titulo: Optional[str] = Query(None, min_length=2, description="Buscar por título"),
        autor: Optional[str] = Query(None, min_length=2, description="Buscar por autor"),
        termo: Optional[str] = Query(None, min_length=2, description="Buscar por título ou autor"),
        ano: Optional[int] = Query(None, description="Filtrar por ano"),
        preco_min: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
        preco_max: Optional[float] = Query(None, ge=0, description="Preço máximo"),
        estoque_min: Optional[int] = Query(None, ge=0, description="Estoque mínimo"),
        estoque_max: Optional[int] = Query(None, ge=0, description="Estoque máximo"),
        skip: int = Query(0, ge=0, description="Registros para pular"),
        limite: int = Query(100, ge=1, le=1000, description="Limite de registros"),
        db: Session = Depends(get_db)
):
    """Busca livros com múltiplos filtros - MELHORADO"""
    try:
        service = LivroService(db)

        if termo:
            # Busca geral
            livros = service.buscar_livros(
                termo=termo,
                skip=skip,
                limite=limite
            )
        else:
            # Busca com filtros específicos
            livros = service.listar_livros(
                autor=autor,
                titulo=titulo,
                ano=ano,
                preco_min=preco_min,
                preco_max=preco_max,
                estoque_min=estoque_min,
                estoque_max=estoque_max,
                skip=skip,
                limite=limite
            )

        return {
            "livros": livros,
            "total_encontrados": len(livros),
            "filtros_aplicados": {
                "termo": termo,
                "titulo": titulo,
                "autor": autor,
                "ano": ano,
                "preco_min": preco_min,
                "preco_max": preco_max,
                "estoque_min": estoque_min,
                "estoque_max": estoque_max
            }
        }
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail="Erro interno na busca")


@router.get("/buscar/termo")
def buscar_livros_por_termo(
        q: str = Query(..., min_length=2, description="Termo de busca"),
        skip: int = Query(0, ge=0),
        limite: int = Query(50, ge=1, le=1000),
        db: Session = Depends(get_db)
):
    """Busca simplificada por termo geral"""
    try:
        service = LivroService(db)
        livros = service.buscar_livros(termo=q, skip=skip, limite=limite)

        return {
            "termo_buscado": q,
            "livros_encontrados": len(livros),
            "livros": livros
        }
    except Exception as e:
        logger.error(f"Erro na busca por termo '{q}': {e}")
        raise HTTPException(status_code=500, detail="Erro interno na busca")


# ---------------------- ESTATÍSTICAS ----------------------
@router.get("/estatisticas/resumo")
def obter_estatisticas(db: Session = Depends(get_db)):
    """Obtém estatísticas dos livros"""
    try:
        service = LivroService(db)
        stats = service.obter_estatisticas()
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter estatísticas")


# ---------------------- STATUS ----------------------
@router.get("/status")
def status_livros():
    """Status do serviço de livros"""
    return {
        "status": "online",
        "service": "LivroService",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints_disponiveis": [
            "GET /livros/ - Página HTML",
            "GET /livros/listar - Lista livros com filtros",
            "GET /livros/{livro_id} - Busca por ID",
            "GET /livros/slug/{slug} - Busca por slug",
            "POST /livros/ - Criar livro",
            "PATCH /livros/{livro_id} - Atualizar livro",
            "DELETE /livros/{livro_id} - Deletar livro",
            "GET /livros/buscar/filtros - Busca avançada",
            "GET /livros/buscar/termo - Busca por termo",
            "GET /livros/estatisticas/resumo - Estatísticas",
            "GET /livros/status - Status do serviço"
        ]
    }


@router.get("/status/completo")
def status_completo_livros(db: Session = Depends(get_db)):
    """Status completo com informações do banco de dados"""
    try:
        # Testa a conexão com o banco fazendo uma consulta simples
        service = LivroService(db)
        total_livros = service.repo.contar_total()

        return {
            "status": "online",
            "service": "LivroService",
            "version": "2.0.0",
            "database_status": "connected",
            "total_livros": total_livros,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no status completo: {e}")
        return {
            "status": "error",
            "service": "LivroService",
            "version": "2.0.0",
            "database_status": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }