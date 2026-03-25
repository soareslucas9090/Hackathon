"""Admin do módulo Financeiro."""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Categoria, Lancamento


@admin.register(Categoria)
class CategoriaAdmin(SimpleHistoryAdmin):
    list_display = ["nome", "usuario", "cor", "created_at"]
    list_filter = ["usuario"]
    search_fields = ["nome", "usuario__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Lancamento)
class LancamentoAdmin(SimpleHistoryAdmin):
    list_display = ["descricao", "tipo", "valor", "data", "categoria", "usuario", "created_at"]
    list_filter = ["tipo", "categoria", "usuario"]
    search_fields = ["descricao", "usuario__username"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "data"
