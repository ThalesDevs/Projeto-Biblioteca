from sqlalchemy.orm import Session
from backend.app.domain.models.usuario.confirmacao_email import ConfirmacaoEmail
from backend.app.domain.models.usuario.usuario import Usuario  # CORRIGIDO: path correto
from datetime import datetime, timedelta
from typing import Optional


class ConfirmacaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar_confirmacao(self, usuario_id: int, tipo: str, horas_expiracao: int = 24,
                          novo_email: str = None) -> ConfirmacaoEmail:
        """Cria nova confirmação de email"""
        token = ConfirmacaoEmail.gerar_token()
        expires_at = datetime.utcnow() + timedelta(hours=horas_expiracao)

        # Invalidar tokens antigos do mesmo tipo para o usuário
        self.db.query(ConfirmacaoEmail).filter(
            ConfirmacaoEmail.usuario_id == usuario_id,
            ConfirmacaoEmail.tipo == tipo,
            ConfirmacaoEmail.usado == False  # noqa
        ).update({ConfirmacaoEmail.usado: True})
        self.db.commit()

        # Criar nova confirmação
        conf = ConfirmacaoEmail(
            usuario_id=usuario_id,
            token=token,
            tipo=tipo,
            novo_email=novo_email,
            expires_at=expires_at,
            usado=False
        )

        self.db.add(conf)
        self.db.commit()
        self.db.refresh(conf)
        return conf

    def obter_por_token(self, token: str) -> Optional[ConfirmacaoEmail]:
        """Busca confirmação por token"""
        return self.db.query(ConfirmacaoEmail).filter(
            ConfirmacaoEmail.token == token
        ).first()

    def marcar_usado(self, token: str) -> bool:
        """Marca token como usado"""
        conf = self.obter_por_token(token)
        if not conf:
            return False

        conf.usado = True
        conf.used_at = datetime.utcnow()
        self.db.commit()
        return True

    def confirmar_email(self, token: str) -> bool:
        """Confirma email usando token"""
        try:
            conf = self.obter_por_token(token)

            # Validações
            if not conf:
                print(f"Token não encontrado: {token}")
                return False

            if conf.usado:
                print(f"Token já foi usado: {token}")
                return False

            if conf.expirou:
                print(f"Token expirado: {token}")
                return False

            # Buscar usuário
            user = self.db.query(Usuario).filter(Usuario.id == conf.usuario_id).first()
            if not user:
                print(f"Usuário não encontrado para ID: {conf.usuario_id}")
                return False

            # Processar confirmação baseado no tipo
            if conf.tipo == "cadastro":
                user.email_confirmado = True
                user.email_confirmado_em = datetime.utcnow()
                print(f"Email confirmado para cadastro: {user.email}")

            elif conf.tipo == "alteracao_email" and conf.novo_email:
                user.email = conf.novo_email
                user.email_confirmado = True
                user.email_confirmado_em = datetime.utcnow()
                print(f"Email alterado para: {conf.novo_email}")

            else:
                print(f"Tipo de confirmação inválido: {conf.tipo}")
                return False

            # Marcar token como usado
            conf.usado = True
            conf.used_at = datetime.utcnow()

            self.db.commit()
            print(f"Confirmação processada com sucesso para usuário {user.id}")
            return True

        except Exception as e:
            print(f"Erro ao confirmar email: {e}")
            self.db.rollback()
            return False

    def limpar_tokens_expirados(self) -> int:
        """Remove tokens expirados da base"""
        try:
            count = self.db.query(ConfirmacaoEmail).filter(
                ConfirmacaoEmail.expires_at < datetime.utcnow()
            ).count()

            self.db.query(ConfirmacaoEmail).filter(
                ConfirmacaoEmail.expires_at < datetime.utcnow()
            ).delete()

            self.db.commit()
            print(f"Removidos {count} tokens expirados")
            return count

        except Exception as e:
            print(f"Erro ao limpar tokens expirados: {e}")
            self.db.rollback()
            return 0

    def obter_confirmacoes_usuario(self, usuario_id: int, tipo: str = None) -> list[ConfirmacaoEmail]:
        """Obtém confirmações de um usuário"""
        query = self.db.query(ConfirmacaoEmail).filter(
            ConfirmacaoEmail.usuario_id == usuario_id
        )

        if tipo:
            query = query.filter(ConfirmacaoEmail.tipo == tipo)

        return query.order_by(ConfirmacaoEmail.created_at.desc()).all()

    def invalidar_tokens_usuario(self, usuario_id: int, tipo: str = None) -> int:
        """Invalida todos os tokens de um usuário"""
        try:
            query = self.db.query(ConfirmacaoEmail).filter(
                ConfirmacaoEmail.usuario_id == usuario_id,
                ConfirmacaoEmail.usado == False  # noqa
            )

            if tipo:
                query = query.filter(ConfirmacaoEmail.tipo == tipo)

            count = query.count()
            query.update({ConfirmacaoEmail.usado: True})

            self.db.commit()
            print(f"Invalidados {count} tokens para usuário {usuario_id}")
            return count

        except Exception as e:
            print(f"Erro ao invalidar tokens: {e}")
            self.db.rollback()
            return 0

    def obter_estatisticas(self) -> dict:
        """Obtém estatísticas das confirmações"""
        try:
            total = self.db.query(ConfirmacaoEmail).count()
            usados = self.db.query(ConfirmacaoEmail).filter(
                ConfirmacaoEmail.usado == True  # noqa
            ).count()
            expirados = self.db.query(ConfirmacaoEmail).filter(
                ConfirmacaoEmail.expires_at < datetime.utcnow(),
                ConfirmacaoEmail.usado == False  # noqa
            ).count()

            return {
                "total": total,
                "usados": usados,
                "expirados": expirados,
                "pendentes": total - usados - expirados
            }

        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                "total": 0,
                "usados": 0,
                "expirados": 0,
                "pendentes": 0
            }