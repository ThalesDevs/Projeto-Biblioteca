from fastapi import APIRouter, Request, Form, Response, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.domain.schemas.token_schema import TokenResponse
from app.utils.auth import get_usuario_context_corrigido
from app.service.auth_service import AuthService
from fastapi.templating import Jinja2Templates

from app.utils.template_utils import get_usuario_context

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["Autenticação"])


from app.domain.schemas.token_schema import TokenResponse
from app.service.auth_service import AuthService

@router.post("/token", response_model=TokenResponse, summary="Gerar token JWT")
def login_token(email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    usuario = auth_service.autenticar_usuario(email, senha)
    token = auth_service.criar_token(usuario)
    return {"access_token": token, "token_type": "bearer"}




@router.get("/login")
def mostrar_formulario_login(request: Request, db: Session = Depends(get_db)):
    context = get_usuario_context_corrigido(request, db)
    return templates.TemplateResponse("login.html", context)


@router.post("/login")
def processar_login(
        response: Response,
        request: Request,
        email: str = Form(...),
        senha: str = Form(...),
        db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    try:
        # Toda a lógica de negócio no service
        usuario = auth_service.autenticar_usuario(email=email, senha=senha)
        token = auth_service.criar_token(usuario)

        # Configuração do cookie também no service
        redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        auth_service.set_auth_cookie(redirect, token)

        return redirect

    except HTTPException as e:
        # Apenas tratamento de resposta na router
        context = {
            "request": request,
            "erro": e.detail,
            "email": email
        }
        return templates.TemplateResponse("login.html", context, status_code=e.status_code)


@router.get("/cadastro")
def mostrar_formulario_cadastro(request: Request, db: Session = Depends(get_db)):
    context = get_usuario_context(request, db)
    return templates.TemplateResponse("cadastro.html", context)


@router.post("/cadastro")
def processar_cadastro(
        request: Request,
        response: Response,
        nome: str = Form(...),
        email: str = Form(...),
        senha: str = Form(...),
        confirmar_senha: str = Form(...),
        db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    try:
        # Lógica de negócio no service
        usuario = auth_service.registrar_usuario(nome, email, senha, confirmar_senha)
        token = auth_service.criar_token(usuario)

        # Configuração do cookie no service
        redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        auth_service.set_auth_cookie(redirect, token)

        return redirect

    except HTTPException as e:
        # Apenas tratamento de resposta na router
        context = {
            "request": request,
            "erro": e.detail,
            "nome": nome,
            "email": email
        }
        return templates.TemplateResponse("cadastro.html", context, status_code=e.status_code)


@router.get("/logout")
def logout(response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService(db)

    # Limpeza do cookie no service
    redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    auth_service.clear_auth_cookie(redirect)

    return redirect