"""Formulários do módulo de configurações de usuário."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import PreferenciaUsuario


class PreferenciaUsuarioForm(forms.ModelForm):
    """
    Formulário para configurar a moeda preferida do usuário.

    As choices do campo moeda_preferida são populadas dinamicamente
    a partir da AwesomeAPI/cache. Usa um widget Select para UX,
    mas o campo é um CharField (a validação de negócio fica em Rules).
    """

    class Meta:
        model = PreferenciaUsuario
        fields = ["moeda_preferida"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = self._get_choices()
        self.fields["moeda_preferida"].widget = forms.Select(
            choices=choices,
            attrs={"class": "form-select form-select-lg"},
        )
        self.fields["moeda_preferida"].label = _("Moeda de exibição")

    def _get_choices(self):
        """
        Monta as choices consultando a API/cache.

        Se a API estiver indisponível, retorna apenas BRL.
        Garante que a moeda atualmente salva sempre apareça na lista,
        evitando falha de validação quando a API está temporariamente fora.
        """
        choices = [("BRL", "BRL — Real Brasileiro")]
        try:
            from common.currency_service import obter_moedas_disponiveis

            moedas = obter_moedas_disponiveis()
            for codigo in sorted(moedas.keys()):
                nome = moedas[codigo]
                choices.append((codigo, f"{codigo} — {nome}"))
        except Exception:
            pass

        # Garantir que o valor atual sempre esteja na lista (resiliência a API down)
        current = self.initial.get("moeda_preferida") or (
            self.instance.moeda_preferida
            if self.instance and self.instance.pk
            else "BRL"
        )
        if current and current not in [c[0] for c in choices]:
            choices.append((current, f"{current} — (moeda atual)"))

        return choices
