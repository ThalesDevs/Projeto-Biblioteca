from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import jwt
from jose.exceptions import JWTError
from datetime import datetime, timedelta

from app.dependencies import get_db
from app.domain.models.usuario.usuario import Usuario  # CORRIGIDO: path correto
from app.service.auth_service import AuthService
from app.service.usuario_service import UsuarioService

SECRET_KEY = "super_secreto_mude_em_producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


def criar_token(usuario: Usuario) -> str:
    """Cria token JWT - CORRIGIDO"""
    expiracao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "nome": usuario.nome,
        "is_admin": getattr(usuario, "is_admin", False),
        "exp": expiracao,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> dict:
    """Verifica token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar se o token expirou
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.utcfromtimestamp(exp):
            raise HTTPException(status_code=401, detail="Token expirado")

        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")


def get_current_user_from_request(request: Request, db: Session) -> Optional[Usuario]:
    """Obtém o usuário atual baseado no token JWT - CORRIGIDO"""
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None

        # Verificar o token
        payload = verificar_token(token)
        usuario_id = int(payload.get("sub"))

        # Buscar usuário no banco usando service
        service = UsuarioService(db)
        usuario = service.obter_usuario_por_id(usuario_id)

        return usuario

    except HTTPException:
        # Token inválido ou expirado
        return None
    except Exception as e:
        # Qualquer outro erro
        print(f"Erro ao obter usuário: {e}")
        return None


def get_current_user_dependency(request: Request, db: Session = Depends(get_db)) -> Optional[Dict[str, Any]]:
    """
    Versão para usar como dependência do FastAPI
    Retorna dados serializáveis, não objetos SQLAlchemy - CORRIGIDO
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
            "is_admin": getattr(usuario, 'is_admin', False),
            "email_confirmado": getattr(usuario, 'email_confirmado', False)
        }

    except Exception as e:
        print(f"Erro ao obter usuário para dependência: {e}")
        return None


def get_usuario_context_corrigido(request: Request, db: Session) -> dict:
    """
    Implementação corrigida para contexto de templates - SEM DUPLICAÇÃO
    """
    context = {"request": request, "usuario_logado": False, "usuario": None}

    try:
        usuario = get_current_user_from_request(request, db)

        if usuario:
            context.update({
                "usuario_logado": True,
                "usuario": usuario
            })

    except Exception as e:
        print(f"Erro em get_usuario_context_corrigido: {e}")
        # Manter context padrão em caso de erro

    return context


def require_authenticated_user(request: Request, db: Session = Depends(get_db)) -> Usuario:
    """
    NOVO: Dependência que EXIGE usuário autenticado
    Levanta HTTPException se não estiver logado
    """
    usuario = get_current_user_from_request(request, db)
    if not usuario:
        raise HTTPException(status_code=401, detail="Autenticação necessária")
    return usuario


def require_admin_user(request: Request, db: Session = Depends(get_db)) -> Usuario:
    """
    NOVO: Dependência que EXIGE usuário admin
    """
    usuario = require_authenticated_user(request, db)
    if not getattr(usuario, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Privilégios de administrador necessários")
    return usuario