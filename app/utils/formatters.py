# app/utils/formatters.py
from decimal import Decimal
from typing import Union

def formatar_preco(valor: Union[float, Decimal, int, None]) -> str:
    """
    Formata um valor numérico como moeda brasileira (R$)

    Args:
        valor: Valor numérico para formatar

    Returns:
        String formatada como R$ X,XX

    Examples:
        >>> formatar_preco(10.99)
        'R$ 10,99'
        >>> formatar_preco(10.9900000000)
        'R$ 10,99'
        >>> formatar_preco(None)
        'R$ 0,00'
    """
    if valor is None:
        return "R$ 0,00"

    # Converter para float e formatar com 2 casas decimais
    valor_float = float(valor)

    # Formatar com 2 casas decimais e trocar ponto por vírgula
    return f"R$ {valor_float:.2f}".replace(".", ",")

def formatar_preco_sem_simbolo(valor: Union[float, Decimal, int, None]) -> str:
    """
    Formata um valor numérico sem o símbolo R$

    Args:
        valor: Valor numérico para formatar

    Returns:
        String formatada como X,XX
    """
    if valor is None:
        return "0,00"

    valor_float = float(valor)
    return f"{valor_float:.2f}".replace(".", ",")

def formatar_data(data):
    """Formata data para formato brasileiro"""
    if data:
        return data.strftime("%d/%m/%Y")
    return ""