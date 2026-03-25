"""Views do módulo Financeiro."""
import json
from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
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
from .helpers import CategoriaHelper, LancamentoHelper
from .models import Categoria, Lancamento


# ─────────────────────────────────────────── Dashboard ───────────────────────

class DashboardView(BasicTemplateView):
    template_name = "financeiro/lancamentos/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        usuario = self.request.user
        ctx["saldo"] = LancamentoHelper.calcular_saldo_usuario(usuario)
        ctx["ultimos"] = LancamentoHelper.ultimos_lancamentos(usuario)

        # dados para o gráfico de barras (receitas x despesas por mês)
        totais_mes = LancamentoHelper.totais_por_mes(usuario)
        ctx["grafico_meses"] = json.dumps(
            [m["mes"].strftime("%m/%Y") for m in totais_mes]
        )
        ctx["grafico_receitas"] = json.dumps(
            [float(m["receitas"]) for m in totais_mes]
        )
        ctx["grafico_despesas"] = json.dumps(
            [float(m["despesas"]) for m in totais_mes]
        )

        # dados para o gráfico de rosca (despesas por categoria)
        por_cat = list(LancamentoHelper.totais_por_categoria(usuario, tipo=Lancamento.TIPO_DESPESA))
        ctx["grafico_cat_labels"] = json.dumps([c["categoria__nome"] for c in por_cat])
        ctx["grafico_cat_valores"] = json.dumps([float(c["total"]) for c in por_cat])
        ctx["grafico_cat_cores"] = json.dumps([c["categoria__cor"] for c in por_cat])

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

    def get_object(self, queryset=None):
        obj = get_object_or_404(Lancamento, pk=self.kwargs["pk"])
        if obj.usuario != self.request.user:
            raise PermissionDenied
        return obj

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
        lancamento = get_object_or_404(Lancamento, pk=pk)
        if lancamento.usuario != request.user:
            raise PermissionDenied
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

    def get_object(self, queryset=None):
        obj = get_object_or_404(Categoria, pk=self.kwargs["pk"])
        if obj.usuario != self.request.user:
            raise PermissionDenied
        return obj

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
        categoria = get_object_or_404(Categoria, pk=pk)
        if categoria.usuario != request.user:
            raise PermissionDenied
        categoria.business.excluir()
        return self.json_success(MSG_EXCLUIDO_SUCESSO)


# ─────────────────────────────────────────── Relatório ───────────────────────

class RelatorioView(BasicTemplateView):
    """Relatório com filtros, gráficos e botão de exportação PDF."""
    template_name = "financeiro/lancamentos/relatorio.html"

    def _get_filtros(self):
        """Extrai e normaliza os filtros da querystring."""
        return {
            "tipo": self.request.GET.get("tipo") or None,
            "categoria": self.request.GET.get("categoria") or None,
            "data_inicio": self.request.GET.get("data_inicio") or None,
            "data_fim": self.request.GET.get("data_fim") or None,
            "busca": self.request.GET.get("busca") or None,
        }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        usuario = self.request.user
        filtros = self._get_filtros()

        lancamentos = LancamentoHelper.listar_por_usuario(usuario, filtros)
        saldo = LancamentoHelper.calcular_saldo_usuario_qs(lancamentos)

        ctx["lancamentos"] = lancamentos
        ctx["saldo"] = saldo
        ctx["categorias"] = CategoriaHelper.listar_por_usuario(usuario)
        ctx["filtros"] = self.request.GET
        ctx["page_title"] = "Relatório"
        return ctx


class RelatorioPDFView(BasicTemplateView):
    """Gera o relatório filtrado como PDF para download."""

    def get(self, request, *args, **kwargs):
        from xhtml2pdf import pisa

        usuario = request.user
        filtros = {
            "tipo": request.GET.get("tipo") or None,
            "categoria": request.GET.get("categoria") or None,
            "data_inicio": request.GET.get("data_inicio") or None,
            "data_fim": request.GET.get("data_fim") or None,
            "busca": request.GET.get("busca") or None,
        }
        lancamentos = LancamentoHelper.listar_por_usuario(usuario, filtros)
        saldo = LancamentoHelper.calcular_saldo_usuario_qs(lancamentos)

        template = get_template("financeiro/lancamentos/relatorio_pdf.html")
        html = template.render({
            "lancamentos": lancamentos,
            "saldo": saldo,
            "filtros": request.GET,
            "usuario": usuario,
        }, request)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="relatorio.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response
