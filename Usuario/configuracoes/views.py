"""Views do módulo de configurações de usuário."""
from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from common.constants import MSG_ATUALIZADO_SUCESSO
from core.views import BasicUpdateView

from .forms import PreferenciaUsuarioForm
from .models import PreferenciaUsuario


class ConfiguracaoMoedaView(BasicUpdateView):
    """
    View para configurar a moeda preferida do usuário.

    GET  → exibe o formulário com dropdown de moedas disponíveis (via API/cache).
    POST → valida e persiste a preferência via camada Business.
    """

    model = PreferenciaUsuario
    form_class = PreferenciaUsuarioForm
    template_name = "usuario/configuracoes/configuracao_moeda.html"
    success_url = reverse_lazy("configuracoes:moeda")

    def get_object(self, queryset=None):
        """Obtém ou cria a PreferenciaUsuario do usuário logado."""
        from .models import PreferenciaUsuario

        return PreferenciaUsuario(usuario=self.request.user).helper.obter_preferencia()

    def form_valid(self, form):
        preferencia = form.save(commit=False)
        preferencia.business.atualizar_moeda()
        messages.success(self.request, MSG_ATUALIZADO_SUCESSO)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Configurações de Moeda"

        try:
            from common.currency_service import obter_cotacoes

            dados = obter_cotacoes()
            if dados:
                data_formatada = datetime.fromisoformat(dados.get("ultima_atualizacao", "")).strftime("%H:%M")
                ctx["ultima_atualizacao"] = data_formatada
                ctx["api_disponivel"] = True
            else:
                ctx["api_disponivel"] = False
        except Exception:
            ctx["api_disponivel"] = False

        return ctx
