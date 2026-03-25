"""Formulários do módulo Financeiro."""
from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from common.widgets import DatePickerInput, MoneyInput

from .models import Categoria, Lancamento


class CategoriaForm(forms.ModelForm):
    """Formulário de criação/edição de Categoria."""

    class Meta:
        model = Categoria
        fields = ["nome", "descricao", "cor"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "cor": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.usuario:
            instance.usuario = self.usuario
        if commit:
            instance.save()
        return instance


class LancamentoForm(forms.ModelForm):
    """Formulário de criação/edição de Lançamento."""

    class Meta:
        model = Lancamento
        fields = ["tipo", "descricao", "valor", "data", "categoria", "observacao"]
        widgets = {
            "data": DatePickerInput(),
            "valor": MoneyInput(),
            "observacao": forms.Textarea(attrs={"rows": 3}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, usuario=None, taxa_moeda=None, simbolo_moeda=None, **kwargs):
        super().__init__(*args, **kwargs)

        verbose_original = self.instance._meta.get_field('valor').verbose_name
        simbolo = simbolo_moeda or "R$"

        self.fields['valor'].label = f"{verbose_original} ({simbolo})"

        self.usuario = usuario
        self.taxa_moeda = Decimal(str(taxa_moeda)) if taxa_moeda is not None else Decimal("1")
        if usuario:
            self.fields["categoria"].queryset = Categoria.objects.filter(
                usuario=usuario
            ).order_by("nome")
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            elif not isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-control")

        # Na edição, converte o valor armazenado (BRL) para a moeda do usuário
        if (
            self.taxa_moeda != Decimal("1")
            and self.instance
            and self.instance.pk
            and self.instance.valor
        ):
            self.initial["valor"] = (self.instance.valor / self.taxa_moeda).quantize(
                Decimal("0.01")
            )

    def clean_valor(self):
        """
        Fallback server-side: converte valor da máscara BR (1.234,56)
        para o formato decimal esperado pelo Python (1234.56).
        Necessário caso o JavaScript esteja desabilitado no client.

        Se o usuário possui uma moeda diferente de BRL, o valor digitado é
        convertido para Real antes de persistir:
            valor_brl = valor_entrada × taxa_inversa (bid)
        """
        valor = self.cleaned_data.get("valor")
        if isinstance(valor, str):
            valor = valor.replace(".", "").replace(",", ".")
            from decimal import InvalidOperation
            try:
                valor = Decimal(valor)
            except InvalidOperation:
                from django.core.exceptions import ValidationError
                raise ValidationError(_("Informe um valor monetário válido."))
        # Converte da moeda do usuário para BRL
        if valor and self.taxa_moeda and self.taxa_moeda != Decimal("1"):
            valor = (valor * self.taxa_moeda).quantize(Decimal("0.01"))
        return valor

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.usuario:
            instance.usuario = self.usuario
        if commit:
            instance.save()
        return instance
