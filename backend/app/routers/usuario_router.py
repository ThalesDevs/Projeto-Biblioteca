from typing import List, Optional
from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
import logging

from backend.app.dependencies import get_db
from backend.app.service.usuario_service import UsuarioService
from backend.app.domain.schemas.cria_usuario import UsuarioCreate, UsuarioOut
from backend.app.utils.template_utils import render_template_with_user, get_current_user_dependency
from backend.app.utils.auth import require_authenticated_user
from fastapi.templating import Jinja2Templates

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

logger = logging.getLogger("UsuarioRouter")
router = APIRouter(tags=["Usuários"])


# --------- Cadastro via JSON (API) ---------
@router.post("/cadastrar", response_model=UsuarioOut)
def cadastrar_usuario_json(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastro via API JSON"""
    try:
        service = UsuarioService(db)
        return service.registrar(usuario_data)
    except Exception as e:
        logger.error(f"Erro no cadastro JSON: {e}")
        raise


# --------- Listar usuários (API) ---------
@router.get("/listar", response_model=List[UsuarioOut])
def listar_usuarios(
        db: Session = Depends(get_db),
        email: Optional[str] = None,
        nome: Optional[str] = None,
        limite: int = 50,
        user_data: Optional[dict] = Depends(get_current_user_dependency)
):
    """Lista usuários - requer autenticação"""
    if not user_data:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        service = UsuarioService(db)
        return service.listar_usuarios(email=email, nome=nome, limite=limite)
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# --------- Perfil do usuário (HTML) ---------
@router.get("/perfil", response_class=HTMLResponse)
def perfil_usuario(request: Request, db: Session = Depends(get_db)):
    """Página de perfil do usuário - CORRIGIDO"""
    try:
        # Usar função auxiliar para obter contexto
        from app.utils.auth import get_usuario_context_corrigido
        context = get_usuario_context_corrigido(request, db)

        if not context.get("usuario_logado"):
            return RedirectResponse(url="/auth/login", status_code=302)

        # Buscar dados adicionais se necessário (pedidos, etc.)
        usuario = context.get("usuario")
        if usuario and hasattr(usuario, "pedidos"):
            context["pedidos"] = usuario.pedidos
        else:
            context["pedidos"] = []

        return templates.TemplateResponse("perfil.html", context)

    except Exception as e:
        logger.error(f"Erro na página de perfil: {e}")
        return RedirectResponse(url="/auth/login?error=Erro interno", status_code=302)


# --------- EDITAR PERFIL (HTML) ---------
@router.get("/editar", response_class=HTMLResponse)
def editar_perfil_html(request: Request, db: Session = Depends(get_db)):
    """Página HTML para editar perfil - CORRIGIDO"""
    try:
        from app.utils.auth import get_usuario_context_corrigido
        context = get_usuario_context_corrigido(request, db)

        if not context.get("usuario_logado"):
            return RedirectResponse(url="/auth/login", status_code=302)

        return templates.TemplateResponse("editar_perfil.html", context)

    except Exception as e:
        logger.error(f"Erro ao carregar página de edição: {e}")
        return RedirectResponse(
            url="/usuarios/perfil?error=Erro ao carregar página",
            status_code=302
        )


@router.post("/editar", response_class=HTMLResponse)
def atualizar_perfil_html(
        request: Request,
        nome: str = Form(...),
        email: str = Form(...),
        db: Session = Depends(get_db)
):
    """Processa o formulário de edição de perfil - CORRIGIDO"""
    try:
        # Verificar autenticação
        from app.utils.auth import get_current_user_from_request
        usuario_logado = get_current_user_from_request(request, db)

        if not usuario_logado:
            return RedirectResponse(url="/auth/login", status_code=302)

        # Usar service para atualizar
        service = UsuarioService(db)
        service.atualizar_dados_basicos(usuario_logado.id, nome, email)

        return RedirectResponse(
            url="/usuarios/perfil?success=Perfil atualizado com sucesso",
            status_code=status.HTTP_302_FOUND
        )

    except HTTPException as e:
        logger.error(f"Erro HTTP ao atualizar perfil: {e.detail}")
        return RedirectResponse(
            url=f"/usuarios/editar?error={e.detail}",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        return RedirectResponse(
            url="/usuarios/editar?error=Erro interno do servidor",
            status_code=status.HTTP_302_FOUND
        )


# --------- Atualizar perfil (API) ---------
@router.put("/perfil", response_model=UsuarioOut)
def atualizar_perfil_usuario(
        usuario_data: UsuarioCreate,
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)
):
    """Atualiza perfil via API"""
    if not user_data:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        service = UsuarioService(db)
        return service.editar_usuario(user_data["id"], usuario_data)
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil via API: {e}")
        raise


# --------- Deletar usuário (API) ---------
@router.delete("/perfil")
def deletar_perfil_usuario(
        db: Session = Depends(get_db),
        user_data: Optional[dict] = Depends(get_current_user_dependency)
):
    """Deleta perfil do usuário"""
    if not user_data:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        service = UsuarioService(db)
        service.deletar_usuario(user_data["id"])
        return {"mensagem": "Usuário deletado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {e}")
        raise


# --------- Utilitários ---------
@router.get("/verificar-email/{email}")
def verificar_email_disponivel(email: str, db: Session = Depends(get_db)):
    """Verifica se email está disponível"""
    try:
        service = UsuarioService(db)
        usuario_existente = service.repo.buscar_por_email(email)
        return {"disponivel": usuario_existente is None}
    except Exception as e:
        logger.error(f"Erro ao verificar email: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/me", response_model=UsuarioOut)
def obter_usuario_atual(
        user_data: dict = Depends(get_current_user_dependency),
        db: Session = Depends(get_db)
):
    """Obtém dados do usuário atual"""
    if not user_data:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        service = UsuarioService(db)
        return service.obter_usuario_por_id(user_data["id"])
    except Exception as e:
        logger.error(f"Erro ao obter usuário atual: {e}")
        raise