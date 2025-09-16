from fastapi import Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.dependencies import get_db
from app.service.usuario_service import UsuarioService
from app.utils.auth import verificar_token


def get_current_user_from_request(request: Request, db: Session) -> Optional[Any]:
    """
    Obtém o usuário atual baseado no token JWT.
    Lê do header Authorization (Bearer token) ou do cookie access_token.
    """
    try:
        # 1️⃣ Pega token do header Authorization
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            # 2️⃣ Se não tiver header, tenta pegar do cookie
            token = request.cookies.get("access_token")

        if not token:
            return None

        # Verifica token
        payload = verificar_token(token)
        usuario_id = int(payload.get("sub"))

        # Buscar usuário no banco
        usuario_service = UsuarioService(db)
        usuario = usuario_service.repo.buscar_por_id(usuario_id)

        return usuario

    except Exception as e:
        print(f"Erro inesperado ao obter usuário atual: {e}")
        return None



def get_current_user_dependency(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Versão para usar como dependência do FastAPI
    Retorna dados serializáveis, não objetos SQLAlchemy
    ✅ CORREÇÃO: Adicionado Depends(get_db)
    """
    try:
        usuario = get_current_user_from_request(request, db)
        if not usuario:
            return None

        # Retornar apenas dados serializáveis
        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "ativo": getattr(usuario, 'ativo', True),
        }

    except Exception as e:
        print(f"Erro ao obter usuário para dependência: {e}")
        return None


def get_usuario_context(request: Request, db: Session) -> Dict[str, Any]:
    """
    Obtém contexto do usuário para templates
    """
    try:
        usuario = get_current_user_from_request(request, db)
        return {
            "request": request,
            "usuario": usuario,
            "usuario_logado": usuario is not None
        }
    except Exception as e:
        print(f"Erro ao obter contexto do usuário: {e}")
        return {
            "request": request,
            "usuario": None,
            "usuario_logado": False
        }


def render_template_with_user(
        templates: Jinja2Templates,
        template_name: str,
        request: Request,
        db: Session,
        status_code: int = 200,
        **kwargs
):
    """
    Renderiza template com contexto do usuário
    """
    try:
        user_context = get_usuario_context(request, db)
        context = {**user_context, **kwargs}
        return templates.TemplateResponse(
            template_name,
            context,
            status_code=status_code
        )
    except Exception as e:
        print(f"Erro ao renderizar template {template_name}: {e}")
        # Fallback em caso de erro
        context = {
            "request": request,
            "usuario": None,
            "usuario_logado": False,
            **kwargs
        }
        return templates.TemplateResponse(
            template_name,
            context,
            status_code=status_code
        )