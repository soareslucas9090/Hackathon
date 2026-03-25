"""
Views do app de autenticação.

Regras:
- LandingPageView: acesso público (sem login).
- CustomLoginView: exibe o formulário de login; redireciona usuário já
  autenticado para o dashboard.
- CustomLogoutView: encerra a sessão e redireciona para a landing page.

Não há regras de negócio nestas views — apenas controle de request/response.
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView


class LandingPageView(TemplateView):
    """
    Exibe a landing page pública do sistema.

    Acessível sem autenticação. Apresenta o sistema e direciona
    o usuário ao login.
    """

    template_name = "usuario/autenticacao/landing.html"


class CustomLoginView(LoginView):
    """
    Exibe o formulário de login e autentica o usuário.

    Usuários já autenticados são redirecionados automaticamente para o
    dashboard (``redirect_authenticated_user = True``).
    O redirecionamento pós-login é controlado por ``LOGIN_REDIRECT_URL``
    no settings ou pelo parâmetro ``next`` na query string.
    """

    template_name = "usuario/autenticacao/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """
    Encerra a sessão do usuário.

    O redirecionamento pós-logout é controlado por ``LOGOUT_REDIRECT_URL``
    no settings (padrão: landing page).
    """
