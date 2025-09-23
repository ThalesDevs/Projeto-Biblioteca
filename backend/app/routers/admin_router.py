from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.dependencies import get_db
from backend.app.domain.schemas.cria_livro import LivroCreate, LivroOut
from backend.app.service.livro_service import LivroService
from backend.app.utils.auth import require_admin_user

router = APIRouter()

# Rota de perfil admin protegida
@router.get("/me", summary="Perfil admin")
def perfil_admin(usuario = Depends(require_admin_user)):
    """
    Retorna informações do usuário admin autenticado.
    """
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "is_admin": getattr(usuario, "is_admin", False)
    }


# Rota para criar livro - somente admin
@router.post("/livros", response_model=LivroOut, status_code=status.HTTP_201_CREATED)
def criar_livro_admin(
    livro: LivroCreate,
    usuario = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """
    Adiciona um novo livro. Apenas administradores podem acessar.
    """
    srv = LivroService(db)
    return srv.adicionar_livro(livro)
