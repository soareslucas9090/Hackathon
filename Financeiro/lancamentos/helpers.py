"""
Camada de Helpers do módulo Financeiro.

Responsabilidade: consultas de leitura (read-only).
Não realiza gravações. Não lança exceções de negócio.
"""
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth

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
        return LancamentoHelper.calcular_saldo_usuario_qs(qs)

    @staticmethod
    def calcular_saldo_usuario_qs(qs):
        """
        Calcula receitas, despesas e saldo a partir de um queryset já filtrado.

        Permite reutilizar o cálculo no relatório com filtros aplicados.
        """
        from .models import Lancamento

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

    @staticmethod
    def totais_por_mes(usuario, ano=None):
        """
        Retorna lista de dicts com receitas e despesas agrupadas por mês.

        Cada item contém ``mes`` (date do primeiro dia), ``receitas`` e ``despesas``.
        Usado para montar o gráfico de barras mensal no dashboard.
        """
        from django.db.models import Case, Value, When
        from .models import Lancamento

        qs = Lancamento.objects.filter(usuario=usuario)
        if ano:
            qs = qs.filter(data__year=ano)

        receitas_mes = (
            qs.filter(tipo=Lancamento.TIPO_RECEITA)
            .annotate(mes=TruncMonth("data"))
            .values("mes")
            .annotate(total=Sum("valor"))
            .order_by("mes")
        )
        despesas_mes = (
            qs.filter(tipo=Lancamento.TIPO_DESPESA)
            .annotate(mes=TruncMonth("data"))
            .values("mes")
            .annotate(total=Sum("valor"))
            .order_by("mes")
        )

        # combina em um dict indexado por mês
        dados = {}
        for r in receitas_mes:
            chave = r["mes"].strftime("%Y-%m")
            dados.setdefault(chave, {"mes": r["mes"], "receitas": Decimal("0"), "despesas": Decimal("0")})
            dados[chave]["receitas"] = r["total"] or Decimal("0")
        for d in despesas_mes:
            chave = d["mes"].strftime("%Y-%m")
            dados.setdefault(chave, {"mes": d["mes"], "receitas": Decimal("0"), "despesas": Decimal("0")})
            dados[chave]["despesas"] = d["total"] or Decimal("0")

        return sorted(dados.values(), key=lambda x: x["mes"])

    @staticmethod
    def totais_por_categoria(usuario, tipo=None):
        """
        Retorna lista de dicts com total agrupado por categoria.

        Usado para montar o gráfico de pizza/donut no dashboard.
        ``tipo`` filtra por "receita" ou "despesa"; se None, considera tudo.
        """
        from .models import Lancamento

        qs = Lancamento.objects.filter(usuario=usuario).select_related("categoria")
        if tipo:
            qs = qs.filter(tipo=tipo)

        return (
            qs.values("categoria__nome", "categoria__cor")
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )
