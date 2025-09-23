import token
from datetime import datetime, timedelta
from fastapi import HTTPException, Response
from sqlalchemy.orm import Session
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

from backend.app.domain.models.usuario.usuario import Usuario
from backend.app.domain.schemas.cria_usuario import UsuarioCreate
from backend.app.service.usuario_service import UsuarioService
from backend.app.repositories.confirmacao_repository import ConfirmacaoRepository
from backend.app.service.email_service import EmailService

# --------- Configurações JWT e senha ---------
SECRET_KEY = "super_secreto_mude_em_producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.usuario_service = UsuarioService(db)
        self.conf_repo = ConfirmacaoRepository(db)
        self.email_service = EmailService()

    def perfil_admin(self, token: str, db: Session) -> Usuario:
        payload = self.verificar_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        usuario = self.usuario_service.repo.buscar_por_id(int(user_id))
        if not usuario or not usuario.is_admin:
            raise HTTPException(status_code=403, detail="Acesso negado. Somente admins.")
        return usuario

    # --------- Registro com confirmação de e-mail ---------
    def registrar_usuario(self, nome: str, email: str, senha: str, confirmar_senha: str = None) -> Usuario:
        if confirmar_senha and senha != confirmar_senha:
            raise HTTPException(status_code=400, detail="Senhas não coincidem")

        # Cria usuário com email_confirmado=False
        usuario_data = UsuarioCreate(nome=nome.strip(), email=email.strip(), senha=senha)
        usuario = self.usuario_service.registrar(usuario_data, email_confirmado=False)

        # Cria token de confirmação e envia e-mail
        confirmacao = self.conf_repo.criar_confirmacao(usuario.id, tipo="cadastro", horas_expiracao=24)
        self.email_service.enviar_confirmacao_cadastro(usuario, confirmacao.token)

        return usuario

    # --------- Autenticação ---------
    def autenticar_usuario(self, email: str, senha: str) -> Usuario:
        usuario = self.usuario_service.repo.buscar_por_email(email)
        if not usuario or not self.verificar_senha(senha, usuario.senha_hash):
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")
        if not usuario.ativo:
            raise HTTPException(status_code=403, detail="Usuário inativo")
        if not usuario.email_confirmado:
            raise HTTPException(status_code=403, detail="Email não confirmado. Verifique sua caixa de entrada.")
        return usuario

    # --------- JWT ---------
    def criar_token(self, usuario: Usuario) -> str:
        expiracao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "nome": usuario.nome,
            "is_admin": usuario.is_admin,
            "exp": expiracao,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verificar_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.utcfromtimestamp(exp):
                raise HTTPException(status_code=401, detail="Token expirado")
            return payload
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

    # --------- Cookies ---------
    def set_auth_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=False,  # True em produção com HTTPS
            path="/"
        )

    def clear_auth_cookie(self, response: Response) -> None:
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True,
            samesite="lax"
        )

    # --------- Obter usuário do token ---------
    def get_usuario_from_token(self, token: str) -> Usuario | None:
        try:
            payload = self.verificar_token(token)
            user_id = payload.get("sub")
            if not user_id:
                return None
            usuario = self.usuario_service.repo.buscar_por_id(int(user_id))
            if not usuario or not usuario.ativo or not usuario.email_confirmado:
                return None
            return usuario
        except HTTPException:
            return None
        except Exception:
            return None

    def validar_sessao(self, token: str) -> bool:
        return self.get_usuario_from_token(token) is not None

    # --------- Utilitários ---------
    def hash_senha(self, senha: str) -> str:
        return pwd_context.hash(senha)

    def verificar_senha(self, senha: str, hash_senha: str) -> bool:
        return pwd_context.verify(senha, hash_senha)

    def obter_dados_token(self, token: str) -> dict | None:
        try:
            return self.verificar_token(token)
        except HTTPException:
            return None
