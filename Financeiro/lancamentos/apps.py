"""Configuração do app de lançamentos financeiros."""
from django.apps import AppConfig


class LancamentosConfig(AppConfig):
    """App responsável por Categoria e Lancamento."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "Financeiro.lancamentos"
    label = "lancamentos"
    verbose_name = "Lançamentos"

    def ready(self):
        """
        Associa as camadas de Business, Helper e Rules aos Models.

        Executado após todos os models estarem carregados, evitando
        importações circulares entre models ↔ business/helpers/rules.
        """
        from .models import Categoria, Lancamento
        from .business import CategoriaBusiness, LancamentoBusiness
        from .helpers import CategoriaHelper, LancamentoHelper
        from .rules import CategoriaRules, LancamentoRules

        Categoria.business_class = CategoriaBusiness
        Categoria.helper_class = CategoriaHelper
        Categoria.rules_class = CategoriaRules

        Lancamento.business_class = LancamentoBusiness
        Lancamento.helper_class = LancamentoHelper
        Lancamento.rules_class = LancamentoRules
