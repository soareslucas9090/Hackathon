"""
Camada de Rules do módulo de configurações de usuário.

Valida regras de negócio relacionadas às preferências do usuário.
"""
from django.utils.translation import gettext as _

from core.exceptions import BusinessRulesExceptions
from core.mixins import ModelRules


class PreferenciaUsuarioRules(ModelRules):
    """Rules de PreferenciaUsuario."""

    def validar_moeda_disponivel(self):
        """
        Verifica se o código de moeda informado é válido.

        - BRL é sempre aceito (moeda base do sistema).
        - Outros códigos são validados contra a lista da AwesomeAPI/cache.
        - Se a API estiver indisponível (cache vazio), a validação é relaxada
          para não bloquear o fluxo do usuário.
        """
        codigo = self.model_instance.moeda_preferida

        if not codigo or not codigo.strip():
            raise BusinessRulesExceptions(_("A moeda preferida não pode ser vazia."))

        if codigo == "BRL":
            return

        try:
            from common.currency_service import obter_moedas_disponiveis

            moedas = obter_moedas_disponiveis()
            # Só valida se a API retornou dados; se estiver indisponível, aceita o código
            if moedas and codigo not in moedas:
                raise BusinessRulesExceptions(
                    _("Moeda '%(codigo)s' não está disponível para conversão. "
                      "Selecione uma moeda da lista.")
                    % {"codigo": codigo}
                )
        except BusinessRulesExceptions:
            raise
        except Exception:
            # API indisponível: não bloquear a operação do usuário
            pass
