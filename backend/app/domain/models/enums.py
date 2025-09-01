# app/domain/models/enums.py
from enum import Enum

class StatusPedido(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

class StatusUsuario(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    SUSPENSO = "SUSPENSO"