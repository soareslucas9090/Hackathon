"""Formulários do módulo Financeiro."""
from django import forms

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

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
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

    def clean_valor(self):
        """
        Fallback server-side: converte valor da máscara BR (1.234,56)
        para o formato decimal esperado pelo Python (1234.56).
        Necessário caso o JavaScript esteja desabilitado no client.
        """
        valor = self.cleaned_data.get("valor")
        if isinstance(valor, str):
            valor = valor.replace(".", "").replace(",", ".")
            from decimal import Decimal, InvalidOperation
            try:
                return Decimal(valor)
            except InvalidOperation:
                from django.core.exceptions import ValidationError
                raise ValidationError("Informe um valor monetário válido.")
        return valor

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.usuario:
            instance.usuario = self.usuario
        if commit:
            instance.save()
        return instance
