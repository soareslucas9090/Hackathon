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


class MoneyInput(forms.NumberInput):
    """
    Widget para campos monetários.

    Adiciona os atributos ``step="0.01"`` e ``min="0"`` para garantir
    entradas com duas casas decimais e valor não-negativo.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("step", "0.01")
        kwargs["attrs"].setdefault("min", "0")
        super().__init__(*args, **kwargs)
