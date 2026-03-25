"""
Template tags e filtros de moeda.

Registrado como builtin em settings.py — disponível em todos os templates
sem necessidade de ``{% load moeda_tags %}``.

Uso::

    {{ saldo.receitas|converter_moeda:moeda_usuario.taxa }}
    → exibe o valor convertido para a moeda do usuário com 2 casas decimais.
"""
from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(name="converter_moeda")
def converter_moeda(valor, taxa):
    """
    Converte um valor em BRL para a moeda do usuário.

    Parâmetros:
        valor : valor numérico em BRL (Decimal, float ou str)
        taxa  : float — taxa de conversão (moeda_usuario.taxa)
                        valor_moeda = valor_brl * taxa

    Retorna Decimal com 2 casas decimais, ou o valor original em caso de erro.

    Exemplos:
        {{ 3000|converter_moeda:0.1957 }}  → 587.10
        {{ 3000|converter_moeda:1.0 }}     → 3000.00
    """
    try:
        valor_decimal = Decimal(str(valor))
        taxa_decimal = Decimal(str(taxa))
        return (valor_decimal * taxa_decimal).quantize(Decimal("0.01"))
    except (InvalidOperation, Exception):
        return valor
