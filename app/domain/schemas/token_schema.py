from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class TokenData(BaseModel):
    email: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# ============= INPUT SCHEMAS =============
class ConfirmarEmailInput(BaseModel):
    token: str = Field(..., description="Token de confirmação")

class ReenviarConfirmacaoInput(BaseModel):
    email: EmailStr = Field(..., description="Email para reenvio")

class AlterarEmailInput(BaseModel):
    novo_email: EmailStr = Field(..., description="Novo email")
    senha: str = Field(..., min_length=6, description="Senha atual para confirmação")

class CadastroComConfirmacaoInput(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo")
    email: EmailStr = Field(..., description="Email")
    senha: str = Field(..., min_length=6, description="Senha")
    confirmar_senha: str = Field(..., min_length=6, description="Confirmação da senha")

# ============= OUTPUT SCHEMAS =============
class ConfirmacaoEmailOut(BaseModel):
    id: int
    usuario_id: int
    tipo: str
    usado: bool
    expires_at: datetime
    created_at: datetime
    expirou: bool

    class Config:
        from_attributes = True

class UsuarioComConfirmacaoOut(BaseModel):
    id: int
    nome: str
    email: str
    email_confirmado: bool
    email_confirmado_em: Optional[datetime] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ConfirmacaoResponse(BaseModel):
    sucesso: bool
    mensagem: str
    usuario: Optional[UsuarioComConfirmacaoOut] = None

# ============= SCHEMAS DE PERFIL COMPLETO =============
class EnderecoInput(BaseModel):
    tipo: str = Field(default="residencial", description="Tipo: residencial, comercial, entrega")
    cep: str = Field(..., pattern=r'^\d{5}-?\d{3}$', description="CEP")
    logradouro: str = Field(..., max_length=200, description="Logradouro")
    numero: str = Field(..., max_length=10, description="Número")
    complemento: Optional[str] = Field(None, max_length=100, description="Complemento")
    bairro: str = Field(..., max_length=100, description="Bairro")
    cidade: str = Field(..., max_length=100, description="Cidade")
    estado: str = Field(..., pattern=r'^[A-Z]{2}$', description="Estado (UF)")
    principal: bool = Field(default=False, description="Endereço principal")

class CartaoInput(BaseModel):
    nome_titular: str = Field(..., max_length=100, description="Nome do titular")
    numero: str = Field(..., pattern=r'^\d{16}$', description="Número do cartão (16 dígitos)")
    bandeira: str = Field(..., description="Bandeira: visa, mastercard, elo, amex")
    mes_vencimento: int = Field(..., ge=1, le=12, description="Mês vencimento (1-12)")
    ano_vencimento: int = Field(..., ge=2025, description="Ano vencimento")
    cvv: str = Field(..., pattern=r'^\d{3,4}$', description="CVV (3 ou 4 dígitos)")
    apelido: Optional[str] = Field(None, max_length=50, description="Apelido do cartão")
    principal: bool = Field(default=False, description="Cartão principal")

class PerfilCompletoInput(BaseModel):
    nome: Optional[str] = Field(None, max_length=100, description="Nome completo")
    cpf: Optional[str] = Field(None, pattern=r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$', description="CPF")
    telefone: Optional[str] = Field(None, max_length=15, description="Telefone")
    data_nascimento: Optional[str] = Field(None, description="Data nascimento (YYYY-MM-DD)")
    endereco: Optional[EnderecoInput] = None
    cartao: Optional[CartaoInput] = None