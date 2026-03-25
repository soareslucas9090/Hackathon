"""
Camada de Business do módulo de configurações de usuário.

Responsabilidade: orquestrar a persistência da preferência de moeda,
chamando a camada de Rules e executando dentro de transaction.atomic().
"""
from django.db import transaction

from core.exceptions import BusinessRulesExceptions, ProcessException, SystemErrorException
from core.mixins import ModelBusiness


class PreferenciaUsuarioBusiness(ModelBusiness):
    """Business de PreferenciaUsuario."""

    def atualizar_moeda(self):
        """Valida e persiste a nova moeda preferida do usuário."""
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_moeda_disponivel()
                self.model_instance.save()
                return self.model_instance
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                "Erro inesperado ao atualizar a preferência de moeda."
            ) from exc
