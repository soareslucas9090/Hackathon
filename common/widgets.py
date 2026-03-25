"""
Widgets personalizados do sistema.

Este módulo centraliza inputs HTML customizados para uso nos Forms
do projeto, garantindo consistência visual com o template Dasher.
"""
from django import forms


class DatePickerInput(forms.DateInput):
    """
    Widget de seleção de data com atributo ``type="date"`` no HTML.

    Garante que o campo de data exiba o seletor nativo do browser
    e use o formato ISO (YYYY-MM-DD) na submissão do formulário.
    """

    input_type = "date"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(*args, **kwargs)


class MoneyInput(forms.TextInput):
    """
    Widget para campos monetários com máscara BR (1.234,56).

    Usa IMask.js no front-end para formatar o valor em tempo real.
    O atributo ``inputmode="decimal"`` garante teclado numérico em mobile.
    No submit, um hidden input envia o valor sem máscara (ex.: 1234.56).
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("inputmode", "decimal")
        kwargs["attrs"].setdefault("placeholder", "0,00")
        kwargs["attrs"].setdefault("autocomplete", "off")
        kwargs["attrs"]["data-money-mask"] = "true"
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        """
        Formata o valor decimal (1234.56) para exibição no input (1.234,56)
        ao carregar o formulário de edição.
        """
        if value is None or value == "":
            return ""
        try:
            import locale as _locale
            cleaned = str(value).replace(",", ".")
            parts = cleaned.split(".")
            integer_part = parts[0]
            decimal_part = parts[1].ljust(2, "0")[:2] if len(parts) > 1 else "00"
            formatted_int = ""
            for i, digit in enumerate(reversed(integer_part)):
                if i > 0 and i % 3 == 0:
                    formatted_int = "." + formatted_int
                formatted_int = digit + formatted_int
            return f"{formatted_int},{decimal_part}"
        except Exception:
            return super().format_value(value)
