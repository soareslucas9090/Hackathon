"""
URL patterns do app de autenticação.

Namespace: ``usuario``

Rotas:
  /login/   → CustomLoginView  (name="login")
  /logout/  → CustomLogoutView (name="logout")

A landing page (/) é registrada diretamente em hackathon/urls.py
para não receber o namespace "usuario", permitindo o uso de
LOGOUT_REDIRECT_URL = "landing" no settings sem namespace.
"""
from django.urls import path

from . import views

app_name = "usuario"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
]
