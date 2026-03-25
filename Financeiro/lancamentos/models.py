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

    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.CharField(max_length=255, blank=True, verbose_name="Descrição")
    cor = models.CharField(
        max_length=7,
        default="#6366f1",
        verbose_name="Cor",
        help_text="Cor hexadecimal, ex.: #6366f1",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categorias",
        verbose_name="Usuário",
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
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
        (TIPO_RECEITA, "Receita"),
        (TIPO_DESPESA, "Despesa"),
    ]

    # Associadas em LancamentosConfig.ready()
    business_class = None
    helper_class = None
    rules_class = None

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name="Tipo",
    )
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor (R$)",
    )
    data = models.DateField(verbose_name="Data")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="lancamentos",
        verbose_name="Categoria",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lancamentos",
        verbose_name="Usuário",
    )
    observacao = models.TextField(blank=True, verbose_name="Observação")

    class Meta:
        verbose_name = "Lançamento"
        verbose_name_plural = "Lançamentos"
        ordering = ["-data", "-created_at"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.descricao} — R$ {self.valor}"
