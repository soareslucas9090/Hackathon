"""
Camada de Helpers do módulo de configurações de usuário.

Responsabilidade: consultas de leitura (read-only) relacionadas às preferências.
"""
from core.mixins import ModelHelper


class PreferenciaUsuarioHelper(ModelHelper):
    """Helpers de consulta para PreferenciaUsuario."""

    def obter_preferencia(self):
        """
        Retorna a PreferenciaUsuario do usuário.

        Se não existir, cria automaticamente com a moeda padrão BRL.
        Nunca retorna None.
        """
        from .models import PreferenciaUsuario

        preferencia, _ = PreferenciaUsuario.objects.get_or_create(
            usuario=self.model_instance.usuario,
            defaults={"moeda_preferida": "BRL"},
        )
        return preferencia
