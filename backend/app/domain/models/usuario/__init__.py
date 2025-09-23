from sqlalchemy.orm import relationship

from backend.app.domain.models.usuario.usuario import Usuario
from backend.app.domain.models.usuario.endereco_usuarios import EnderecoUsuario
from backend.app.domain.models.usuario.usuario import Usuario
from backend.app.domain.models.usuario.cartao_credito import CartaoCredito
from backend.app.domain.models.usuario.usuario import Usuario
from backend.app.domain.models.usuario.confirmacao_email import ConfirmacaoEmail


Usuario.confirmacoes_email = relationship(
    ConfirmacaoEmail,
    back_populates="usuario",
    cascade="all, delete-orphan"
)

