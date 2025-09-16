
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.repositories.confirmacao_repository import ConfirmacaoRepository

router = APIRouter(prefix="/email", tags=["Email"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/confirmar", response_class=HTMLResponse)
def confirmar_email(request: Request, token: str, db: Session = Depends(get_db)):
    repo = ConfirmacaoRepository(db)
    ok = repo.confirmar_email(token)
    if ok:
        return templates.TemplateResponse("confirmacao_sucesso.html", {"request": request})
    return templates.TemplateResponse("confirmacao_falha.html", {"request": request}, status_code=400)
