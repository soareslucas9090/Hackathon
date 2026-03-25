"""Configuração do app de autenticação de usuários."""
from django.apps import AppConfig


class AutenticacaoConfig(AppConfig):
    """App responsável pelo login, logout e landing page."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "Usuario.autenticacao"
    label = "autenticacao"
    verbose_name = "Autenticação"
