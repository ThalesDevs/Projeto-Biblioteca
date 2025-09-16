from sqlalchemy.orm import relationship

from app.domain.models.usuario.usuario import Usuario
from app.domain.models.usuario.endereco_usuarios import EnderecoUsuario
from app.domain.models.usuario.usuario import Usuario
from app.domain.models.usuario.cartao_credito import CartaoCredito
from app.domain.models.usuario.usuario import Usuario
from app.domain.models.usuario.confirmacao_email import ConfirmacaoEmail


Usuario.confirmacoes_email = relationship(
    ConfirmacaoEmail,
    back_populates="usuario",
    cascade="all, delete-orphan"
)

