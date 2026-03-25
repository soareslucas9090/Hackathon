"""Views do módulo Financeiro."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from common.constants import (
    MSG_CRIADO_SUCESSO,
    MSG_ATUALIZADO_SUCESSO,
    MSG_EXCLUIDO_SUCESSO,
)
from core.views import (
    BasicActionView,
    BasicCreateView,
    BasicDeleteView,
    BasicTableView,
    BasicTemplateView,
    BasicUpdateView,
)

from .forms import CategoriaForm, LancamentoForm
from .helpers import LancamentoHelper
from .models import Categoria, Lancamento


# ─────────────────────────────────────────── Dashboard ───────────────────────

class DashboardView(BasicTemplateView):
    template_name = "financeiro/lancamentos/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["saldo"] = LancamentoHelper.calcular_saldo_usuario(self.request.user)
        ctx["ultimos"] = LancamentoHelper.ultimos_lancamentos(self.request.user)
        ctx["page_title"] = "Dashboard"
        return ctx


# ─────────────────────────────────────────── Lançamentos ─────────────────────

class LancamentoListView(BasicTableView):
    model = Lancamento
    template_name = "financeiro/lancamentos/lancamento_lista.html"
    partial_template_name = "financeiro/lancamentos/partials/lancamento_tabela.html"

    def get_queryset(self):
        filtros = {
            "tipo": self.request.GET.get("tipo"),
            "categoria": self.request.GET.get("categoria"),
            "data_inicio": self.request.GET.get("data_inicio") or None,
            "data_fim": self.request.GET.get("data_fim") or None,
            "busca": self.request.GET.get("busca"),
        }
        return LancamentoHelper.listar_por_usuario(self.request.user, filtros)

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return [self.partial_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"] = Categoria.objects.filter(usuario=self.request.user).order_by("nome")
        ctx["filtros"] = self.request.GET
        ctx["page_title"] = "Lançamentos"
        return ctx


class LancamentoCreateView(BasicCreateView):
    model = Lancamento
    form_class = LancamentoForm
    template_name = "financeiro/lancamentos/lancamento_form.html"
    success_url = reverse_lazy("financeiro:lancamento-lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        lancamento = form.save(commit=False)
        lancamento.usuario = self.request.user
        lancamento.business.criar()
        messages.success(self.request, MSG_CRIADO_SUCESSO)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Novo Lançamento"
        return ctx


class LancamentoUpdateView(BasicUpdateView):
    model = Lancamento
    form_class = LancamentoForm
    template_name = "financeiro/lancamentos/lancamento_form.html"
    success_url = reverse_lazy("financeiro:lancamento-lista")

    def get_queryset(self):
        return Lancamento.objects.filter(usuario=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        lancamento = form.save(commit=False)
        lancamento.business.atualizar()
        messages.success(self.request, MSG_ATUALIZADO_SUCESSO)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Editar Lançamento"
        return ctx


class LancamentoDeleteView(BasicActionView):
    def post(self, request, pk, *args, **kwargs):
        lancamento = get_object_or_404(Lancamento, pk=pk, usuario=request.user)
        lancamento.business.excluir()
        return self.json_success(MSG_EXCLUIDO_SUCESSO)


# ─────────────────────────────────────────── Categorias ──────────────────────

class CategoriaListView(BasicTableView):
    model = Categoria
    template_name = "financeiro/lancamentos/categoria_lista.html"
    partial_template_name = "financeiro/lancamentos/partials/categoria_tabela.html"

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user).order_by("nome")

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return [self.partial_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Categorias"
        return ctx


class CategoriaCreateView(BasicCreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "financeiro/lancamentos/categoria_form.html"
    success_url = reverse_lazy("financeiro:categoria-lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        categoria = form.save(commit=False)
        categoria.usuario = self.request.user
        categoria.business.criar()
        messages.success(self.request, MSG_CRIADO_SUCESSO)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Nova Categoria"
        return ctx


class CategoriaUpdateView(BasicUpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "financeiro/lancamentos/categoria_form.html"
    success_url = reverse_lazy("financeiro:categoria-lista")

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        categoria = form.save(commit=False)
        categoria.business.atualizar()
        messages.success(self.request, MSG_ATUALIZADO_SUCESSO)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Editar Categoria"
        return ctx


class CategoriaDeleteView(BasicActionView):
    def post(self, request, pk, *args, **kwargs):
        categoria = get_object_or_404(Categoria, pk=pk, usuario=request.user)
        categoria.business.excluir()
        return self.json_success(MSG_EXCLUIDO_SUCESSO)


# ─────────────────────────────────────────── Relatório ───────────────────────

class RelatorioView(BasicTemplateView):
    """Placeholder para o Passo 4 (exportação PDF/Excel)."""
    template_name = "financeiro/lancamentos/relatorio.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Relatório"
        return ctx
