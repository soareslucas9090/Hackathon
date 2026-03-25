---
applyTo: "core/**"
---

# Instructions — Módulo `core`

## Propósito

O `core` é o núcleo técnico da aplicação. Ele **não contém regras de negócio**. Sua responsabilidade é:

- Fornecer classes base para Models, Views e Mixins.
- Definir e centralizar as exceções personalizadas do sistema.
- Centralizar o tratamento de erros HTTP (400, 403, 404, 500).
- Disponibilizar constantes técnicas.

## Arquivos e responsabilidades

| Arquivo | Responsabilidade |
|---|---|
| `exceptions.py` | `BusinessRulesExceptions`, `ProcessException`, `SystemErrorException` |
| `mixins.py` | `BusinessModelMixin`, `HelperModelMixin`, `RulesModelMixin`, `ModelBusiness`, `ModelHelper`, `ModelRules` |
| `models.py` | `BasicModel` — herda de `Model` e adiciona `created_at`, `updated_at`, `history` |
| `views.py` | `BasicDetailView`, `BasicTableView`, `BasicCreateView`, `BasicUpdateView`, `BasicDeleteView`, `BasicActionView`, `BasicTemplateView` |
| `constants.py` | Constantes técnicas (ex: paginação, tamanhos máximos) |
| `error_handlers.py` | `handler400`, `handler403`, `handler404`, `handler500` |

## Regras

- **NUNCA** adicione regras de negócio aqui. Este módulo é agnóstico ao domínio.
- Exceções devem ser instanciadas com mensagem amigável ao usuário.
- Novos BasicViews devem herdar `LoginRequiredMixin` + `ExceptionHandlerMixin`.
- O `BasicActionView` lida exclusivamente com AJAX e retorna `JsonResponse`.

## Exceções — Padrão de uso

```python
# rules.py
from core.exceptions import BusinessRulesExceptions

class MinhaRules(ModelRules):
    def validar_algo(self):
        if not condicao:
            raise BusinessRulesExceptions("Mensagem amigável.")

# business.py
from core.exceptions import ProcessException, SystemErrorException

class MeuBusiness(ModelBusiness):
    def criar(self):
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_algo()
                self.model_instance.save()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException("Erro inesperado.") from exc
```

## Mixins de composição — Padrão de injeção

```python
# models.py
class MeuModel(BasicModel, BusinessModelMixin, HelperModelMixin, RulesModelMixin):
    business_class = None  # Injetado em apps.py
    helper_class = None
    rules_class = None

# apps.py
class MeuAppConfig(AppConfig):
    def ready(self):
        from .models import MeuModel
        from .business import MeuBusiness
        MeuModel.business_class = MeuBusiness
```

## BasicViews disponíveis

| Classe | Base Django | Uso típico |
|---|---|---|
| `BasicDetailView` | `DetailView` | Exibir detalhe de um registro |
| `BasicTableView` | `ListView` | Listagem com suporte AJAX partial |
| `BasicCreateView` | `CreateView` | Formulário de criação |
| `BasicUpdateView` | `UpdateView` | Formulário de edição |
| `BasicDeleteView` | `DeleteView` | Confirmação de exclusão |
| `BasicActionView` | `View` | Ação AJAX (exclusão, toggle, etc.) |
| `BasicTemplateView` | `TemplateView` | Página genérica (dashboard, relatório) |
