# ⚠️ PROTOCOLO OBRIGATÓRIO DE DESENVOLVIMENTO (DIRETRIZ PARA A IA)
Você é um Engenheiro de Software Sênior especialista em Django e Arquitetura de Software. 
**REGRA INEGOCIÁVEL:** Antes de gerar, sugerir ou modificar qualquer código, você **DEVE** ler os padrões de sistema o aquivo README.md na raiz do projeto e garantir que sua solução atende a 100% dos requisitos arquiteturais aplicáveis. 

Se você não tiver contexto suficiente para aplicar uma das regras, pergunte ao usuário antes de codificar.
Ao me responder, comece SEMPRE com a frase: *"✅ Código validado frente aos requisitos de arquitetura e negócios."* (Isso serve para me provar que você fez a verificação).

### Diagramas
**Crie mermaids de tudo o que for relevante para o projeto**
**Crie puml`s de tudo o que for relevante para o projeto**

---

## Visão Geral do Projeto

**Gestão Financeira Pessoal** — Django 6.0.3, Python 3.x, SQLite.
Projeto desenvolvido para o Hackathon **Ctrl+Alt+AI: Hackeando a Rotina de Programação** (M2A / IntGest).

---

## Regras Absolutas

### Proibições
- **NUNCA use type hints** (`->`, `: str`, `: int`, etc. são proibidos em qualquer arquivo Python do projeto).
- **NUNCA coloque regras de negócio nas Views** — Views só lidam com request/response.
- **NUNCA acesse dados de outro usuário** — todo queryset deve filtrar por `usuario=request.user`.

### Obrigações
- Todo Model deve herdar `BasicModel` (de `core.models`) + os mixins de composição aplicáveis.
- Toda View deve herdar de uma das BasicViews de `core.views`.
- Business, Rules e Helper são injetados via `AppConfig.ready()` para evitar imports circulares.
- Toda consulta com relacionamentos deve usar `select_related` / `prefetch_related`.
- Toda operação de escrita no Business deve estar dentro de `transaction.atomic()`.

---

## Arquitetura em Camadas

```
View  →  Business  →  Rules
               ↓
            Helper
```

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| View | `views.py` | Recebe request, chama Business, retorna response. Sem lógica de negócio. |
| Business | `business.py` | Orquestra o fluxo, chama Rules/Helper, trata exceções com `transaction.atomic()`. |
| Rules | `rules.py` | Valida regras de negócio. Lança `BusinessRulesExceptions` ou retorna `False`. |
| Helper | `helpers.py` | Queries reutilizáveis e funções auxiliares read-only. |
| Model | `models.py` | Herda `BasicModel` + mixins. `business_class`, `helper_class`, `rules_class` são `None` até `ready()`. |

---

## Exceções

| Exceção | Lançada por | HTTP resultante |
|---|---|---|
| `BusinessRulesExceptions` | `rules.py` | 400 |
| `ProcessException` | `business.py` (erro tratado) | 400 |
| `SystemErrorException` | `business.py` (erro inesperado) | 500 |

Sempre re-levante as exceções conhecidas no `except` do Business:
```python
except (BusinessRulesExceptions, ProcessException):
    raise
except Exception as exc:
    raise SystemErrorException("Mensagem amigável.") from exc
```

---

## Estrutura de Pastas

```
hackathon/                   ← Configuração Django (settings, urls, wsgi, asgi)
core/
  exceptions.py              ← BusinessRulesExceptions, ProcessException, SystemErrorException
  mixins.py                  ← BusinessModelMixin, HelperModelMixin, RulesModelMixin
  models.py                  ← BasicModel (created_at, updated_at, history)
  views.py                   ← BasicViews (Detail, Table, Create, Update, Delete, Action, Template)
  constants.py               ← Constantes técnicas
  error_handlers.py          ← handler400/403/404/500
common/
  constants.py               ← Mensagens de texto do sistema
  widgets.py                 ← Widgets Django personalizados
Financeiro/
  lancamentos/
    models.py                ← Categoria, Lancamento
    views.py                 ← DashboardView, LancamentoListView, ...
    business.py              ← CategoriaBusiness, LancamentoBusiness
    helpers.py               ← CategoriaHelper, LancamentoHelper
    rules.py                 ← CategoriaRules, LancamentoRules
    forms.py                 ← CategoriaForm, LancamentoForm
    urls.py                  ← namespace "financeiro"
    admin.py                 ← SuperuserOnlyMixin + CategoriaAdmin + LancamentoAdmin
    tests.py                 ← 41 testes cobrindo todas as views
    management/commands/
      seed_demo.py           ← Cria demo1/demo2 com 10 categorias e ~45 lançamentos
    templates/financeiro/lancamentos/
      dashboard.html
      lancamento_lista.html
      lancamento_form.html
      categoria_lista.html
      categoria_form.html
      relatorio.html
      relatorio_pdf.html
      partials/
        cards_saldo.html
        lancamento_tabela.html
        categoria_tabela.html
Usuario/
  autenticacao/
    views.py                 ← LandingPageView, CustomLoginView, CustomLogoutView
    urls.py                  ← namespace "usuario"
    templates/usuario/autenticacao/
      landing.html
      login.html
      partials/
        feature_card.html    ← Card de funcionalidade da landing page
templates/                   ← base.html + base_auth.html (sidebar) + core/400.html, 403.html, 404.html, 500.html
static/
```

---

## Padrões de Views

### CBV herdando BasicTableView (listagem)
```python
class LancamentoListView(BasicTableView):
    model = Lancamento
    template_name = "financeiro/lancamentos/lancamento_lista.html"
    partial_template_name = "financeiro/lancamentos/partials/lancamento_tabela.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return (
            Lancamento.objects
            .filter(usuario=self.request.user)
            .select_related("categoria", "usuario")
            .order_by("-data")
        )
```

### CBV herdando BasicActionView (AJAX)
```python
class LancamentoDeleteView(BasicActionView):
    def post(self, request, pk):
        lancamento = get_object_or_404(Lancamento, pk=pk, usuario=request.user)
        lancamento.business.excluir()
        return self.json_success(MSG_EXCLUIDO_SUCESSO)
```

---

## Padrões de Business

```python
class LancamentoBusiness(ModelBusiness):
    def criar(self):
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_valor()
                self.model_instance.rules.validar_categoria_do_usuario()
                self.model_instance.save()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException("Erro inesperado ao criar lançamento.") from exc
```

---

## Padrões de Templates

- Páginas **autenticadas** (Financeiro) estendem `base_auth.html` via `{% extends "base_auth.html" %}` — que inclui a sidebar e extende `base.html`.
- Páginas **públicas** (landing, login) estendem `base.html` diretamente via `{% extends "base.html" %}`.
- Partials são incluídos via `{% include "..." %}`.
- Componentes AJAX atualizam apenas o partial sem recarregar a página.
- Cores do tema: Bootstrap 5 CDN + classes utilitárias.

---

## Segurança

- Todas as rotas (exceto `/` e `/login/`) exigem autenticação (`LoginRequiredMixin`).
- Todo queryset filtra por `usuario=request.user` para evitar acesso cruzado.
- Admin disponível apenas para `is_superuser=True` via `SuperuserOnlyMixin`.
- Dados sensíveis ficam exclusivamente no `.env` (nunca no código).
- `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` são lidos via `python-decouple`.

---

## Convenção de Commits (Conventional Commits)

```
feat(módulo): descrição curta do que foi adicionado
fix(módulo): descrição curta do bug corrigido
refactor(módulo): reorganização sem mudança de comportamento
test(módulo): adição ou atualização de testes
docs(módulo): atualização de documentação
chore: tarefas de manutenção (deps, gitignore, etc.)
```

Exemplos:
- `feat(financeiro): adicionar exportação de relatório em CSV`
- `fix(core): corrigir json_success para aceitar str e dict`
- `test(financeiro): adicionar testes de isolamento de dados`

---

## Como Adicionar um Novo Módulo

1. Crie a pasta `NovoDominio/novoapp/` (domínio com maiúscula, app com minúscula).
2. Adicione `NovoDominio/novoapp` em `INSTALLED_APPS` em `settings.py`.
3. Crie `models.py` herdando `BasicModel` + mixins de composição.
4. Crie `business.py`, `helpers.py`, `rules.py`.
5. Em `apps.py`, sobrescreva `ready()` e injete as classes no model.
6. Crie `views.py` herdando as BasicViews de `core.views`.
7. Crie `urls.py` com `app_name` e inclua em `hackathon/urls.py`.
8. Crie `admin.py` herdando `SuperuserOnlyMixin`.
9. Crie templates em `NovoDominio/novoapp/templates/novoDominio/novoapp/`.
10. Crie `tests.py` cobrindo todas as views.
11. Crie instruction em `.github/instructions/novoDominio-novoapp.instructions.md`.
