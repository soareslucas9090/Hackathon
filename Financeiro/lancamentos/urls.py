"""URLs do módulo Financeiro."""
from django.urls import path

from . import views

app_name = "financeiro"

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Análise financeira IA
    path("analise/", views.AnaliseFinanceiraView.as_view(), name="analise-financeira"),
    path("analise/pdf/", views.AnaliseFinanceiraPDFView.as_view(), name="analise-pdf"),
    # Lançamentos
    path("lancamentos/", views.LancamentoListView.as_view(), name="lancamento-lista"),
    path("lancamentos/novo/", views.LancamentoCreateView.as_view(), name="lancamento-criar"),
    path("lancamentos/importar/", views.ImportarPlanilhaView.as_view(), name="lancamento-importar"),
    path("lancamentos/modelo/", views.DownloadModeloPlanilhaView.as_view(), name="lancamento-modelo"),
    path("lancamentos/<int:pk>/editar/", views.LancamentoUpdateView.as_view(), name="lancamento-editar"),
    path("lancamentos/<int:pk>/excluir/", views.LancamentoDeleteView.as_view(), name="lancamento-excluir"),
    # Categorias
    path("categorias/", views.CategoriaListView.as_view(), name="categoria-lista"),
    path("categorias/nova/", views.CategoriaCreateView.as_view(), name="categoria-criar"),
    path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria-editar"),
    path("categorias/<int:pk>/excluir/", views.CategoriaDeleteView.as_view(), name="categoria-excluir"),
    # Relatório
    path("relatorio/", views.RelatorioView.as_view(), name="relatorio"),
    path("relatorio/pdf/", views.RelatorioPDFView.as_view(), name="relatorio-pdf"),
]
