# backend/houter.py

from fastapi import APIRouter

from backend.app.utils import auth

# Cria o router principal
router = APIRouter()

# Aqui você inclui todos os routers separados
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(usuarios_router, prefix="/usuarios", tags=["Usuários"])
router.include_router(livros_router, prefix="/livros", tags=["Livros"])
