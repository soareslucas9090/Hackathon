"""Configuração do app de configurações de usuário."""
from django.apps import AppConfig


class ConfiguracoesConfig(AppConfig):
    """App responsável pelas preferências do usuário."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "Usuario.configuracoes"
    label = "configuracoes"
    verbose_name = "Configurações"

    def ready(self):
        """
        Associa as camadas de Business, Helper e Rules ao Model PreferenciaUsuario.

        Executado após todos os models estarem carregados, evitando
        importações circulares entre models ↔ business/helpers/rules.
        """
        from .models import PreferenciaUsuario
        from .business import PreferenciaUsuarioBusiness
        from .helpers import PreferenciaUsuarioHelper
        from .rules import PreferenciaUsuarioRules

        PreferenciaUsuario.business_class = PreferenciaUsuarioBusiness
        PreferenciaUsuario.helper_class = PreferenciaUsuarioHelper
        PreferenciaUsuario.rules_class = PreferenciaUsuarioRules
