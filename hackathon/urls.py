"""
URL configuration for hackathon project.

Rotas raiz do projeto. Cada módulo possui seu próprio urls.py incluído aqui.
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # As rotas de cada módulo serão incluídas nos próximos passos:
    # path("", include("Usuario.autenticacao.urls")),
    # path("financeiro/", include("Financeiro.lancamentos.urls")),
]

# ─── Handlers de erro personalizados ────────────────────────────────────────
handler400 = "core.error_handlers.handler400"
handler403 = "core.error_handlers.handler403"
handler404 = "core.error_handlers.handler404"
handler500 = "core.error_handlers.handler500"

