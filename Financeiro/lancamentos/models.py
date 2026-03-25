"""
Models do módulo Financeiro.

Hierarquia:
- Categoria: agrupa lançamentos por tema (ex.: Alimentação, Transporte).
- Lancamento: representa uma receita ou despesa do usuário.

Ambos estendem ``BasicModel`` (auditoria + histórico) e os mixins de
composição. As classes de Business, Helper e Rules são associadas em
``apps.py::LancamentosConfig.ready()``, evitando importações circulares.
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BasicModel
from core.mixins import BusinessModelMixin, HelperModelMixin, RulesModelMixin

User = get_user_model()


class Categoria(BasicModel, BusinessModelMixin, HelperModelMixin, RulesModelMixin):
    """
    Categoria financeira do usuário.

    Cada categoria pertence exclusivamente ao usuário que a criou.
    O par (nome, usuario) é único, garantido por ``unique_together``.
    """

    # Associadas em LancamentosConfig.ready()
    business_class = None
    helper_class = None
    rules_class = None

    nome = models.CharField(max_length=100, verbose_name=_("Nome"))
    descricao = models.CharField(max_length=255, blank=True, verbose_name=_("Descrição"))
    cor = models.CharField(
        max_length=7,
        default="#6366f1",
        verbose_name=_("Cor"),
        help_text=_("Cor hexadecimal, ex.: #6366f1"),
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="categorias",
        verbose_name=_("Usuário"),
    )

    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")
        ordering = ["nome"]
        unique_together = [("nome", "usuario")]

    def __str__(self):
        return self.nome


class Lancamento(BasicModel, BusinessModelMixin, HelperModelMixin, RulesModelMixin):
    """
    Lançamento financeiro (receita ou despesa) do usuário.

    O campo ``tipo`` determina se o lançamento representa uma entrada
    (receita) ou saída (despesa) de dinheiro.
    Cada lançamento pertence a um único usuário e a uma categoria.
    """

    TIPO_RECEITA = "receita"
    TIPO_DESPESA = "despesa"
    TIPO_CHOICES = [
        (TIPO_RECEITA, _("Receita")),
        (TIPO_DESPESA, _("Despesa")),
    ]

    # Associadas em LancamentosConfig.ready()
    business_class = None
    helper_class = None
    rules_class = None

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name=_("Tipo"),
    )
    descricao = models.CharField(max_length=255, verbose_name=_("Descrição"))
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Valor"),
    )
    data = models.DateField(verbose_name=_("Data"))
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="lancamentos",
        verbose_name=_("Categoria"),
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="lancamentos",
        verbose_name=_("Usuário"),
    )
    observacao = models.TextField(blank=True, verbose_name=_("Observação"))

    class Meta:
        verbose_name = _("Lançamento")
        verbose_name_plural = _("Lançamentos")
        ordering = ["-data", "-created_at"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.descricao} — R$ {self.valor}"
