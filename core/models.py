"""
Modelos base do sistema.

Todos os Models do projeto devem herdar de ``BasicModel`` para garantir
os campos de auditoria (created_at, updated_at) e o histórico de alterações
via django-simple-history.
"""
from django.db import models
from simple_history.models import HistoricalRecords


class BasicModel(models.Model):
    """
    Model abstrato base do sistema.

    Fornece:
    - ``created_at``: data/hora de criação do registro (preenchida automaticamente).
    - ``updated_at``: data/hora da última alteração (atualizada automaticamente).
    - ``history``: histórico completo de alterações via django-simple-history.

    Para ativar as camadas de Business, Helper e Rules na instância, inclua
    os mixins correspondentes junto com a herança deste Model::

        from core.models import BasicModel
        from core.mixins import BusinessModelMixin, HelperModelMixin, RulesModelMixin

        class Lancamento(BasicModel, BusinessModelMixin, HelperModelMixin, RulesModelMixin):
            business_class = LancamentoBusiness
            helper_class   = LancamentoHelper
            rules_class    = LancamentoRules
            ...
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
