"""
Views base do sistema (Class-Based Views).

Todas as Views do projeto devem herdar das classes aqui definidas.
Elas centralizam:
- Proteção de acesso (login obrigatório).
- Tratamento padronizado das exceções do sistema
  (BusinessRulesExceptions → 400, ProcessException → 400,
   Http404 → 404, PermissionDenied → 403, SystemErrorException → 500).
- Padrões de resposta AJAX para o BasicActionView.

Hierarquia::

    BasicDetailView   → DetailView  + LoginRequiredMixin + tratamento de erros
    BasicTableView    → ListView    + LoginRequiredMixin + tratamento de erros
    BasicCreateView   → CreateView  + LoginRequiredMixin + tratamento de erros
    BasicUpdateView   → UpdateView  + LoginRequiredMixin + tratamento de erros
    BasicDeleteView   → DeleteView  + LoginRequiredMixin + tratamento de erros
    BasicActionView   → View        + LoginRequiredMixin + resposta JSON para AJAX
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from core.exceptions import (
    BusinessRulesExceptions,
    ProcessException,
    SystemErrorException,
)

logger = logging.getLogger(__name__)


class ExceptionHandlerMixin:
    """
    Mixin que centraliza o tratamento das exceções do sistema nas Views.

    Deve ser herdado pelas BasicViews para garantir que todas as exceções
    personalizadas sejam traduzidas no código HTTP correto.
    """

    def dispatch(self, request, *args, **kwargs):
        """Intercepta a requisição e trata exceções de forma centralizada."""
        try:
            return super().dispatch(request, *args, **kwargs)
        except (BusinessRulesExceptions, ProcessException) as exc:
            logger.warning("Erro de negócio/processo: %s", exc.message)
            return self._handle_business_error(request, exc)
        except PermissionDenied as exc:
            logger.warning("Acesso negado: %s", exc)
            return self._handle_permission_denied(request, exc)
        except Http404 as exc:
            logger.warning("Registro não encontrado: %s", exc)
            return self._handle_not_found(request, exc)
        except SystemErrorException as exc:
            logger.error("Erro de sistema: %s", exc.message, exc_info=True)
            return self._handle_system_error(request, exc)
        except Exception as exc:
            logger.error("Erro inesperado: %s", exc, exc_info=True)
            return self._handle_system_error(
                request, SystemErrorException(str(exc))
            )

    def _handle_business_error(self, request, exc):
        """Retorna resposta de erro 400 (erro de negócio tratado)."""
        from django.shortcuts import render
        return render(request, "core/400.html", {"error": exc.message}, status=400)

    def _handle_permission_denied(self, request, exc):
        """Retorna resposta de erro 403 (acesso não autorizado)."""
        from django.shortcuts import render
        return render(request, "core/403.html", {"error": str(exc)}, status=403)

    def _handle_not_found(self, request, exc):
        """Retorna resposta de erro 404 (registro não encontrado)."""
        from django.shortcuts import render
        return render(request, "core/404.html", {"error": str(exc)}, status=404)

    def _handle_system_error(self, request, exc):
        """Retorna resposta de erro 500 (erro inesperado de sistema)."""
        from django.shortcuts import render
        return render(request, "core/500.html", {"error": exc.message}, status=500)


class BasicDetailView(LoginRequiredMixin, ExceptionHandlerMixin, DetailView):
    """
    View base para exibição de detalhe de um objeto.

    Garante que apenas usuários autenticados acessem a página
    e que o tratamento de erros seja uniforme.
    """


class BasicTableView(LoginRequiredMixin, ExceptionHandlerMixin, ListView):
    """
    View base para listagem de objetos em tabela.

    Garante que apenas usuários autenticados acessem a página
    e que o tratamento de erros seja uniforme.
    """


class BasicCreateView(LoginRequiredMixin, ExceptionHandlerMixin, CreateView):
    """
    View base para criação de objetos.

    A regra de negócio NÃO deve ser colocada aqui; deve ser delegada
    à camada Business via método ``form_valid``.
    """


class BasicUpdateView(LoginRequiredMixin, ExceptionHandlerMixin, UpdateView):
    """
    View base para atualização de objetos.

    A regra de negócio NÃO deve ser colocada aqui; deve ser delegada
    à camada Business via método ``form_valid``.
    """


class BasicDeleteView(LoginRequiredMixin, ExceptionHandlerMixin, DeleteView):
    """
    View base para exclusão de objetos.

    A regra de negócio NÃO deve ser colocada aqui; deve ser delegada
    à camada Business via método ``form_valid`` ou ``delete``.
    """


class BasicActionView(LoginRequiredMixin, ExceptionHandlerMixin, View):
    """
    View base para ações executadas via AJAX (ex.: exclusão dinâmica em tabela).

    Sempre retorna JSON. Em caso de sucesso, retorna ``{"success": true}``.
    Em caso de erro, retorna ``{"success": false, "error": "mensagem"}``.

    Exemplo de uso::

        class ExcluirLancamentoView(BasicActionView):
            def post(self, request, pk):
                lancamento = get_object_or_404(Lancamento, pk=pk, usuario=request.user)
                lancamento.business.excluir()
                return self.json_success()
    """

    def dispatch(self, request, *args, **kwargs):
        """Intercepta e converte exceções em respostas JSON."""
        try:
            return super().dispatch(request, *args, **kwargs)
        except (BusinessRulesExceptions, ProcessException) as exc:
            logger.warning("Erro de negócio/processo (AJAX): %s", exc.message)
            return self.json_error(exc.message, status=400)
        except PermissionDenied as exc:
            logger.warning("Acesso negado (AJAX): %s", exc)
            return self.json_error(str(exc), status=403)
        except Http404 as exc:
            logger.warning("Não encontrado (AJAX): %s", exc)
            return self.json_error(str(exc), status=404)
        except SystemErrorException as exc:
            logger.error("Erro de sistema (AJAX): %s", exc.message, exc_info=True)
            return self.json_error(exc.message, status=500)
        except Exception as exc:
            logger.error("Erro inesperado (AJAX): %s", exc, exc_info=True)
            return self.json_error(
                "Erro inesperado. Contate o suporte.", status=500
            )

    def json_success(self, data: dict = None, status: int = 200) -> JsonResponse:
        """Retorna uma resposta JSON de sucesso."""
        payload = {"success": True}
        if data:
            payload.update(data)
        return JsonResponse(payload, status=status)

    def json_error(self, message: str, status: int = 400) -> JsonResponse:
        """Retorna uma resposta JSON de erro."""
        return JsonResponse({"success": False, "error": message}, status=status)
