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

    def listar_por_usuario(self, busca=None):
        """Retorna todas as categorias do usuário ordenadas por nome."""
        from .models import Categoria

        qs = Categoria.objects.filter(
            usuario=self.model_instance.usuario
        ).order_by("nome")
        if busca:
            qs = qs.filter(nome__icontains=busca)
        return qs


class LancamentoHelper(ModelHelper):
    """Helpers de consulta para Lançamento."""

    def listar_por_usuario(self, filtros=None):
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

        qs = Lancamento.objects.filter(
            usuario=self.model_instance.usuario
        ).select_related("categoria", "usuario")
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

    def calcular_saldo_usuario(self):
        """
        Retorna um dict com ``receitas``, ``despesas`` e ``saldo`` do usuário.

        Todos os valores são :class:`~decimal.Decimal`.
        """
        from .models import Lancamento
        from common.util import calcular_saldo_por_queryset

        qs = Lancamento.objects.filter(usuario=self.model_instance.usuario)
        return calcular_saldo_por_queryset(qs)

    def ultimos_lancamentos(self, n=5):
        """Retorna os ``n`` lançamentos mais recentes do usuário."""
        from .models import Lancamento

        return (
            Lancamento.objects.filter(usuario=self.model_instance.usuario)
            .select_related("categoria", "usuario")
            .order_by("-data", "-created_at")[:n]
        )

    def totais_por_mes(self, ano=None):
        """
        Retorna lista de dicts com receitas e despesas agrupadas por mês.

        Cada item contém ``mes`` (date do primeiro dia), ``receitas`` e ``despesas``.
        Usado para montar o gráfico de barras mensal no dashboard.
        """
        from .models import Lancamento

        qs = Lancamento.objects.filter(usuario=self.model_instance.usuario)
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

    def totais_por_categoria(self, tipo=None):
        """
        Retorna lista de dicts com total agrupado por categoria.

        Usado para montar o gráfico de pizza/donut no dashboard.
        ``tipo`` filtra por "receita" ou "despesa"; se None, considera tudo.
        """
        from .models import Lancamento

        qs = Lancamento.objects.filter(
            usuario=self.model_instance.usuario
        ).select_related("categoria")
        if tipo:
            qs = qs.filter(tipo=tipo)

        return (
            qs.values("categoria__nome", "categoria__cor")
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )

    def obter_lancamentos_periodo(self, meses=3):
        """
        Retorna receitas e despesas dos últimos ``meses`` meses formatadas
        como texto resumido para envio a APIs de análise.
        """
        from datetime import date
        from dateutil.relativedelta import relativedelta
        from .models import Lancamento

        usuario = self.model_instance.usuario
        data_inicio = date.today() - relativedelta(months=meses)

        qs = (
            Lancamento.objects.filter(
                usuario=usuario,
                data__gte=data_inicio,
            )
            .select_related("categoria")
            .order_by("data")
        )

        receitas = []
        despesas = []
        for lanc in qs:
            linha = (
                f"{lanc.data.strftime('%d/%m/%Y')} | "
                f"{lanc.descricao} | "
                f"{lanc.categoria.nome} | "
                f"R$ {lanc.valor}"
            )
            if lanc.tipo == Lancamento.TIPO_RECEITA:
                receitas.append(linha)
            else:
                despesas.append(linha)

        return {
            "receitas": receitas,
            "despesas": despesas,
            "total_registros": len(receitas) + len(despesas),
        }

    def obter_taxa_moeda(self):
        """
        Retorna a taxa_inversa (bid) da moeda preferida do usuário autenticado.

        A taxa_inversa representa quantos BRL valem 1 unidade da moeda escolhida.
        Fórmulas de conversão:
          valor_brl      = valor_na_moeda × taxa_inversa
          valor_na_moeda = valor_brl      ÷ taxa_inversa

        Retorna Decimal("1") para BRL ou em caso de falha (conversão neutra).
        """
        usuario = self.model_instance.usuario
        try:
            from Usuario.configuracoes.models import PreferenciaUsuario
            from common.currency_service import obter_cotacoes

            preferencia = PreferenciaUsuario(usuario=usuario).helper.obter_preferencia()
            codigo = preferencia.moeda_preferida if preferencia else "BRL"

            if codigo == "BRL":
                return Decimal("1")

            dados = obter_cotacoes()
            if dados:
                info = dados.get("cotacoes", {}).get(codigo)
                if info:
                    bid = Decimal(str(info["bid"]))
                    if bid > 0:
                        return bid
        except Exception:
            pass
        return Decimal("1")

    def obter_simbolo_moeda(self):
        """
        Retorna o símbolo monetário da moeda preferida do usuário.
        Exemplo: 'R$' para BRL, 'US$' para USD, '€' para EUR.
        Retorna 'R$' como fallback.
        """
        usuario = self.model_instance.usuario
        try:
            from Usuario.configuracoes.models import PreferenciaUsuario
            from common.currency_service import SIMBOLOS_MOEDAS

            preferencia = PreferenciaUsuario(usuario=usuario).helper.obter_preferencia()
            codigo = preferencia.moeda_preferida if preferencia else "BRL"
            return SIMBOLOS_MOEDAS.get(codigo, codigo)
        except Exception:
            pass
        return "R$"
