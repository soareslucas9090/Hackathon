"""
Camada de Helpers do módulo Financeiro.

Responsabilidade: consultas de leitura (read-only).
Não realiza gravações. Não lança exceções de negócio.
"""
from decimal import Decimal

from django.db.models import Sum

from core.mixins import ModelHelper


class CategoriaHelper(ModelHelper):
    """Helpers de consulta para Categoria."""

    # ------------------------------------------------------------------ static
    @staticmethod
    def listar_por_usuario(usuario):
        """Retorna todas as categorias do usuário ordenadas por nome."""
        from .models import Categoria

        return Categoria.objects.filter(usuario=usuario).order_by("nome")


class LancamentoHelper(ModelHelper):
    """Helpers de consulta para Lançamento."""

    # ------------------------------------------------------------------ static
    @staticmethod
    def listar_por_usuario(usuario, filtros=None):
        """
        Retorna lançamentos do usuário aplicando filtros opcionais.

        Parâmetros aceitos em ``filtros``:
        - ``tipo``        : "receita" | "despesa"
        - ``categoria``   : pk da categoria
        - ``data_inicio`` : date
        - ``data_fim``    : date
        - ``busca``       : texto parcial pesquisado em ``descricao``
        """
        from .models import Lancamento

        qs = Lancamento.objects.filter(usuario=usuario).select_related(
            "categoria", "usuario"
        )
        if filtros:
            if filtros.get("tipo"):
                qs = qs.filter(tipo=filtros["tipo"])
            if filtros.get("categoria"):
                qs = qs.filter(categoria_id=filtros["categoria"])
            if filtros.get("data_inicio"):
                qs = qs.filter(data__gte=filtros["data_inicio"])
            if filtros.get("data_fim"):
                qs = qs.filter(data__lte=filtros["data_fim"])
            if filtros.get("busca"):
                qs = qs.filter(descricao__icontains=filtros["busca"])
        return qs

    @staticmethod
    def calcular_saldo_usuario(usuario):
        """
        Retorna um dict com ``receitas``, ``despesas`` e ``saldo`` do usuário.

        Todos os valores são :class:`~decimal.Decimal`.
        """
        from .models import Lancamento

        qs = Lancamento.objects.filter(usuario=usuario)
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

    @staticmethod
    def ultimos_lancamentos(usuario, n=5):
        """Retorna os ``n`` lançamentos mais recentes do usuário."""
        from .models import Lancamento

        return (
            Lancamento.objects.filter(usuario=usuario)
            .select_related("categoria", "usuario")
            .order_by("-data", "-created_at")[:n]
        )
