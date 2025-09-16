from app.database import SessionLocal
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.service.auth_service import AuthService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_usuario_autenticado(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")

    auth_service = AuthService(db)
    usuario = auth_service.get_usuario_from_token(token)

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return usuario