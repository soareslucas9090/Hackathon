"""URLs do módulo de configurações de usuário."""
from django.urls import path

from . import views

app_name = "configuracoes"

urlpatterns = [
    path("moeda/", views.ConfiguracaoMoedaView.as_view(), name="moeda"),
]
