from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.app.domain.models.usuario.usuario import Usuario
from backend.app.domain.schemas.cria_usuario import UsuarioCreate
from backend.app.repositories.usuario_repository import UsuarioRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)
        self.db = db

    # --------- Cadastro ---------
    def registrar(self, usuario_data: UsuarioCreate) -> Usuario:
        """Registra novo usuário - CORRIGIDO"""
        if self.repo.buscar_por_email(usuario_data.email):
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

        # Hash da senha
        usuario_data.senha_hash = pwd_context.hash(usuario_data.senha)
        return self.repo.criar_usuario(usuario_data)

    def listar_usuarios(self, email: Optional[str] = None, nome: Optional[str] = None, limite: int = 50) -> List[
        Usuario]:
        """Lista usuários com filtros opcionais"""
        query = self.db.query(Usuario)
        if email:
            query = query.filter(Usuario.email.ilike(f"%{email}%"))
        if nome:
            query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
        return query.limit(limite).all()

    def editar_usuario(self, usuario_id: int, usuario_data: UsuarioCreate) -> Usuario:
        """Edita usuário existente"""
        # Verificar se email já existe (exceto para o próprio usuário)
        usuario_atual = self.repo.buscar_por_id(usuario_id)
        if not usuario_atual:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if usuario_data.email != usuario_atual.email:
            usuario_existente = self.repo.buscar_por_email(usuario_data.email)
            if usuario_existente:
                raise HTTPException(status_code=400, detail="E-mail já cadastrado")

        # Hash da senha se foi alterada
        if usuario_data.senha:
            usuario_data.senha_hash = pwd_context.hash(usuario_data.senha)

        usuario = self.repo.atualizar_usuario(usuario_id, usuario_data)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario

    def deletar_usuario(self, usuario_id: int) -> None:
        """Deleta usuário"""
        usuario = self.repo.deletar_usuario(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # --------- Atualizar dados básicos ---------
    def atualizar_dados_basicos(self, usuario_id: int, nome: str, email: str) -> Usuario:
        """Atualiza apenas nome e email (para formulário HTML)"""
        usuario = self.repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Verificar se email já existe (exceto para o próprio usuário)
        if email != usuario.email:
            usuario_existente = self.repo.buscar_por_email(email)
            if usuario_existente:
                raise HTTPException(status_code=400, detail="E-mail já cadastrado")

        # Atualizar dados
        usuario_atualizado = self.repo.atualizar_dados_pessoais(usuario_id, nome=nome, email=email)
        if not usuario_atualizado:
            raise HTTPException(status_code=500, detail="Erro ao atualizar usuário")

        return usuario_atualizado

    # --------- Obter usuário por ID ---------
    def obter_usuario_por_id(self, usuario_id: int) -> Usuario:
        """Obtém usuário por ID com tratamento de erro"""
        usuario = self.repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario

    def obter_usuario_por_email(self, email: str) -> Usuario:
        """Obtém usuário por email com tratamento de erro"""
        usuario = self.repo.buscar_por_email(email)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario

    # --------- Confirmação de email ---------
    def confirmar_email_usuario(self, usuario_id: int) -> Usuario:
        """Confirma email do usuário"""
        usuario = self.repo.confirmar_email(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario

    def alterar_email_usuario(self, usuario_id: int, novo_email: str) -> Usuario:
        """Altera email do usuário"""
        # Verificar se novo email já existe
        if self.repo.buscar_por_email(novo_email):
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

        usuario = self.repo.alterar_email(usuario_id, novo_email)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario

    # --------- Validação de senha ---------
    def verificar_senha(self, usuario_id: int, senha: str) -> bool:
        """Verifica se a senha está correta"""
        usuario = self.repo.buscar_por_id(usuario_id)
        if not usuario:
            return False
        return pwd_context.verify(senha, usuario.senha_hash)

    def alterar_senha(self, usuario_id: int, senha_atual: str, nova_senha: str) -> Usuario:
        """Altera senha do usuário"""
        usuario = self.repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if not pwd_context.verify(senha_atual, usuario.senha_hash):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")

        # Criar um UsuarioCreate apenas com os dados necessários
        usuario_data = UsuarioCreate(
            nome=usuario.nome,
            email=usuario.email,
            senha=nova_senha
        )
        usuario_data.senha_hash = pwd_context.hash(nova_senha)

        usuario_atualizado = self.repo.atualizar_usuario(usuario_id, usuario_data)
        if not usuario_atualizado:
            raise HTTPException(status_code=500, detail="Erro ao alterar senha")

        return usuario_atualizado