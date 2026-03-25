"""Admin do módulo de configurações de usuário.

Acesso restrito exclusivamente a superusuários.
"""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import PreferenciaUsuario


class SuperuserOnlyMixin:
    """Mixin que restringe o acesso ao admin somente a superusuários."""

    def has_module_perms(self, request, app_label=None):
        return request.user.is_active and request.user.is_superuser

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser


@admin.register(PreferenciaUsuario)
class PreferenciaUsuarioAdmin(SuperuserOnlyMixin, SimpleHistoryAdmin):
    """Admin de PreferenciaUsuario — histórico completo via simple-history."""

    list_display = ["usuario", "moeda_preferida", "created_at", "updated_at"]
    list_filter = ["moeda_preferida"]
    search_fields = ["usuario__username", "usuario__email"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["usuario__username"]
