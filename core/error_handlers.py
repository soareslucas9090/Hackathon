"""
Handlers de erro globais do projeto.

Referenciados em ``hackathon/urls.py`` via handler400, handler403,
handler404 e handler500 para exibir páginas de erro personalizadas.
"""
from django.shortcuts import render


def handler400(request, exception=None):
    """Retorna a página de erro 400 (requisição inválida)."""
    return render(request, "core/400.html", {"error": str(exception) if exception else None}, status=400)


def handler403(request, exception=None):
    """Retorna a página de erro 403 (acesso negado)."""
    return render(request, "core/403.html", {"error": str(exception) if exception else None}, status=403)


def handler404(request, exception=None):
    """Retorna a página de erro 404 (página não encontrada)."""
    return render(request, "core/404.html", {"error": str(exception) if exception else None}, status=404)


def handler500(request):
    """Retorna a página de erro 500 (erro interno do servidor)."""
    return render(request, "core/500.html", {}, status=500)
