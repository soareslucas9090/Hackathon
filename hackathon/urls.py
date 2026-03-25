"""
URL configuration for hackathon project.

Rotas raiz do projeto. Cada módulo possui seu próprio urls.py incluído aqui.

Estrutura:
  /            → LandingPageView (público, name="landing")
  /login/      → CustomLoginView (público, namespace "usuario")
  /logout/     → CustomLogoutView (requer sessão, namespace "usuario")
  /financeiro/ → URLs do módulo Financeiro (adicionado no Passo 3)
  /admin/      → Django Admin (apenas superusuários)
"""
from django.contrib import admin
from django.urls import include, path

from Usuario.autenticacao.views import LandingPageView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Landing page pública — sem namespace para manter LOGOUT_REDIRECT_URL = "landing"
    path("", LandingPageView.as_view(), name="landing"),
    # Módulo de autenticação (namespace "usuario")
    path("", include("Usuario.autenticacao.urls")),
    # Módulo Financeiro
    path("financeiro/", include("Financeiro.lancamentos.urls")),
]

# ─── Handlers de erro personalizados ────────────────────────────────────────
handler400 = "core.error_handlers.handler400"
handler403 = "core.error_handlers.handler403"
handler404 = "core.error_handlers.handler404"
handler500 = "core.error_handlers.handler500"


