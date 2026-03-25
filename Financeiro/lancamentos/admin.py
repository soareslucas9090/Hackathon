"""Admin do módulo Financeiro.

Acesso restrito exclusivamente a superusuários.
"""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Categoria, Lancamento


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


@admin.register(Categoria)
class CategoriaAdmin(SuperuserOnlyMixin, SimpleHistoryAdmin):
    """Admin de Categoria — histórico completo via simple-history."""

    list_display = ["nome", "usuario", "cor", "created_at"]
    list_filter = ["usuario"]
    search_fields = ["nome", "usuario__username"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["usuario", "nome"]


@admin.register(Lancamento)
class LancamentoAdmin(SuperuserOnlyMixin, SimpleHistoryAdmin):
    """Admin de Lançamento — histórico completo via simple-history."""

    list_display = ["descricao", "tipo", "valor", "data", "categoria", "usuario", "created_at"]
    list_filter = ["tipo", "categoria", "usuario"]
    search_fields = ["descricao", "usuario__username"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "data"
    ordering = ["-data", "-created_at"]
