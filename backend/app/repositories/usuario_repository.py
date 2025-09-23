from sqlalchemy.orm import Session
from app.domain.models.usuario.usuario import Usuario
from app.domain.schemas.cria_usuario import UsuarioCreate
from typing import Optional
from datetime import datetime


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca usuário por ID"""
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def criar_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        """Cria novo usuário - CORRIGIDO para aceitar UsuarioCreate"""
        usuario = Usuario(
            nome=usuario_data.nome,
            email=usuario_data.email,
            senha_hash=usuario_data.senha_hash,
            email_confirmado=False,
            ativo=True
        )

        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)

        return usuario

    def atualizar_dados_pessoais(self, usuario_id: int, nome: str, email: str) -> Optional[Usuario]:
        """Atualiza dados pessoais do usuário"""
        usuario = self.buscar_por_id(usuario_id)
        if not usuario:
            return None

        usuario.nome = nome
        usuario.email = email
        usuario.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(usuario)

        return usuario

    def atualizar_usuario(self, usuario_id: int, usuario_data: UsuarioCreate) -> Optional[Usuario]:
        """Atualiza usuário com UsuarioCreate - CORRIGIDO"""
        usuario = self.buscar_por_id(usuario_id)
        if not usuario:
            return None

        usuario.nome = usuario_data.nome
        usuario.email = usuario_data.email

        # Se senha foi alterada
        if hasattr(usuario_data, 'senha_hash') and usuario_data.senha_hash:
            usuario.senha_hash = usuario_data.senha_hash

        usuario.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(usuario)

        return usuario

    def deletar_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Deleta usuário"""
        usuario = self.buscar_por_id(usuario_id)
        if not usuario:
            return None

        self.db.delete(usuario)
        self.db.commit()
        return usuario

    def confirmar_email(self, usuario_id: int) -> Optional[Usuario]:
        """Confirma o email do usuário"""
        usuario = self.buscar_por_id(usuario_id)
        if not usuario:
            return None

        usuario.email_confirmado = True
        usuario.email_confirmado_em = datetime.utcnow()

        self.db.commit()
        self.db.refresh(usuario)

        return usuario

    def alterar_email(self, usuario_id: int, novo_email: str) -> Optional[Usuario]:
        """Altera email do usuário"""
        usuario = self.buscar_por_id(usuario_id)
        if not usuario:
            return None

        usuario.email = novo_email
        usuario.email_confirmado = True
        usuario.email_confirmado_em = datetime.utcnow()
        usuario.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(usuario)

        return usuario