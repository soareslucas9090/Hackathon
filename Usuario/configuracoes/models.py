"""
Models do módulo de configurações de usuário.

PreferenciaUsuario: armazena a moeda de exibição preferida do usuário.
Relacionamento 1:1 com User; criado automaticamente no primeiro acesso via Helper.
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.mixins import BusinessModelMixin, HelperModelMixin, RulesModelMixin
from core.models import BasicModel

User = get_user_model()


class PreferenciaUsuario(BasicModel, BusinessModelMixin, HelperModelMixin, RulesModelMixin):
    """
    Preferências do usuário.

    Atualmente armazena a moeda de exibição preferida (código ISO, ex: "BRL", "USD").
    Os valores financeiros são sempre armazenados em BRL; a conversão é feita
    em tempo real durante a exibição com base nesse campo.
    """

    # Associadas em ConfiguracoesConfig.ready()
    business_class = None
    helper_class = None
    rules_class = None

    moeda_preferida = models.CharField(
        max_length=10,
        default="BRL",
        verbose_name=_("Moeda preferida"),
        help_text=_("Código ISO da moeda de exibição (ex: BRL, USD, EUR)."),
    )
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="preferencia",
        verbose_name=_("Usuário"),
    )

    class Meta:
        verbose_name = _("Preferência do Usuário")
        verbose_name_plural = _("Preferências dos Usuários")
        ordering = ["usuario__username"]

    def __str__(self):
        return f"{self.usuario.username} — {self.moeda_preferida}"
