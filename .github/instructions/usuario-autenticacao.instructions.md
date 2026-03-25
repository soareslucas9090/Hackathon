---
applyTo: "Usuario/**"
---

# Instructions — Módulo `Usuario/autenticacao`

## Propósito

Módulo responsável pela autenticação do usuário e pela landing page pública. 

Não contém models próprios — usa `django.contrib.auth.User` diretamente.

## Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `views.py` | `LandingPageView`, `CustomLoginView`, `CustomLogoutView` |
| `urls.py` | Rotas com namespace `"usuario"`: `/login/`, `/logout/` |
| `templates/autenticacao/landing.html` | Landing page pública com apresentação do sistema |
| `templates/autenticacao/login.html` | Formulário de login |

## Rotas

| URL | View | Nome | Acesso |
|---|---|---|---|
| `/` | `LandingPageView` | `landing` | Público |
| `/login/` | `CustomLoginView` | `usuario:login` | Público |
| `/logout/` | `CustomLogoutView` | `usuario:logout` | Autenticado |

## Configurações relevantes (settings.py)

```python
LOGIN_URL = "usuario:login"
LOGIN_REDIRECT_URL = "financeiro:dashboard"
LOGOUT_REDIRECT_URL = "landing"
```

## Regras

- `LandingPageView` e `CustomLoginView` são públicas — **não** herdam `LoginRequiredMixin`.
- `CustomLogoutView` deve exigir POST para evitar logout via GET (segurança CSRF).
- Após login bem-sucedido, redirecionar para `financeiro:dashboard`.
- Após logout, redirecionar para `landing`.
- Não criar models neste módulo — autenticação usa o `User` do Django nativo.

## Padrão de View

```python
from django.contrib.auth.views import LoginView
from core.views import BasicTemplateView

class LandingPageView(TemplateView):
    template_name = "autenticacao/landing.html"

class CustomLoginView(LoginView):
    template_name = "autenticacao/login.html"
```

## Segurança

- Nunca exibir informações de outro usuário neste módulo.
- Em caso de falha de login, não revelar se o usuário existe (Django LoginView já trata isso).
- Dados do formulário de login nunca devem ser logados.
