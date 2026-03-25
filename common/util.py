"""
Funções utilitárias puras reutilizáveis no projeto.

Não dependem de instância de model. Recebem dados já processados
e retornam resultados calculados.
"""
from decimal import Decimal

from django.db.models import Sum


def calcular_saldo_por_queryset(qs):
    """
    Calcula receitas, despesas e saldo a partir de um queryset de Lancamento.

    Permite reutilizar o cálculo em qualquer contexto com filtros já aplicados.
    Retorna um dict com ``receitas``, ``despesas`` e ``saldo`` em
    :class:`~decimal.Decimal`.
    """
    from Financeiro.lancamentos.models import Lancamento

    receitas = (
        qs.filter(tipo=Lancamento.TIPO_RECEITA).aggregate(t=Sum("valor"))["t"]
        or Decimal("0.00")
    )
    despesas = (
        qs.filter(tipo=Lancamento.TIPO_DESPESA).aggregate(t=Sum("valor"))["t"]
        or Decimal("0.00")
    )
    return {
        "receitas": receitas,
        "despesas": despesas,
        "saldo": receitas - despesas,
    }
