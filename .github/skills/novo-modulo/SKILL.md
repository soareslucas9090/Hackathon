---
name: novo-modulo
description: |
  Skill para criar um novo domínio/app Django seguindo a arquitetura em camadas do projeto.
  USE PARA: criar um novo módulo do zero com models, business, rules, helpers, views,
  templates, admin, testes e instructions. Inclui passo a passo completo e commits sugeridos.
---

# SKILL — Adicionar Novo Módulo Django

## Quando usar esta skill

Use quando for necessário criar um novo domínio/app Django seguindo a
arquitetura em camadas do projeto.

## Checklist de criação

Antes de gerar qualquer código, confirme:
- [ ] Tenho o nome do domínio (letra maiúscula) e do app (letra minúscula)?
- [ ] Li o `README.md` e o `copilot-instructions.md`?
- [ ] O novo módulo não duplica funcionalidade existente?

## Passo a passo

### 1. Criar a estrutura de pastas

```
NovoDominio/
  __init__.py
  novoapp/
    __init__.py
    apps.py
    models.py
    views.py
    business.py
    helpers.py
    rules.py
    forms.py
    urls.py
    admin.py
    tests.py
    templates/
      novodominio/novoapp/
        lista.html
        form.html
        partials/
          tabela.html
    management/
      __init__.py
      commands/
        __init__.py
```

### 2. `models.py` — herdar BasicModel + mixins

```python
from core.models import BasicModel
from core.mixins import BusinessModelMixin, HelperModelMixin, RulesModelMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class MeuModel(BasicModel, BusinessModelMixin, HelperModelMixin, RulesModelMixin):
    business_class = None
    helper_class = None
    rules_class = None

    # campos...
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meus_models")

    class Meta:
        verbose_name = "Meu Model"
        verbose_name_plural = "Meus Models"
        ordering = ["-created_at"]
```

### 3. `apps.py` — injetar classes em ready()

```python
from django.apps import AppConfig

class NovoappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "NovoDominio.novoapp"
    verbose_name = "Novo App"

    def ready(self):
        from .models import MeuModel
        from .business import MeuBusiness
        from .helpers import MeuHelper
        from .rules import MeuRules

        MeuModel.business_class = MeuBusiness
        MeuModel.helper_class = MeuHelper
        MeuModel.rules_class = MeuRules
```

### 4. `business.py` — orquestrar fluxo

```python
from django.db import transaction
from core.mixins import ModelBusiness
from core.exceptions import BusinessRulesExceptions, ProcessException, SystemErrorException

class MeuBusiness(ModelBusiness):
    def criar(self):
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_algo()
                self.model_instance.save()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException("Erro inesperado ao criar.") from exc

    def atualizar(self):
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_algo()
                self.model_instance.save()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException("Erro inesperado ao atualizar.") from exc

    def excluir(self):
        try:
            with transaction.atomic():
                self.model_instance.delete()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException("Erro inesperado ao excluir.") from exc
```

### 5. `rules.py` — validações de negócio

```python
from core.mixins import ModelRules
from core.exceptions import BusinessRulesExceptions

class MeuRules(ModelRules):
    def validar_algo(self):
        if not condicao:
            raise BusinessRulesExceptions("Mensagem amigável da regra.")
```

### 6. `helpers.py` — queries reutilizáveis

```python
from core.mixins import ModelHelper

class MeuHelper(ModelHelper):
    def listar_por_usuario(self, usuario):
        return (
            self.model_instance.__class__.objects
            .filter(usuario=usuario)
            .select_related("usuario")
            .order_by("-created_at")
        )
```

### 7. `views.py` — sem regras de negócio

```python
from django.shortcuts import get_object_or_404
from core.views import BasicTableView, BasicCreateView, BasicUpdateView, BasicActionView
from .models import MeuModel
from .forms import MeuForm

class MeuModelListView(BasicTableView):
    model = MeuModel
    template_name = "novodominio/novoapp/lista.html"
    partial_template_name = "novodominio/novoapp/partials/tabela.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return (
            MeuModel.objects
            .filter(usuario=self.request.user)
            .select_related("usuario")
            .order_by("-created_at")
        )

class MeuModelCreateView(BasicCreateView):
    model = MeuModel
    form_class = MeuForm
    template_name = "novodominio/novoapp/form.html"
    success_url = "novodominio:lista"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.usuario = self.request.user
        obj.business.criar()
        return redirect(self.success_url)

class MeuModelDeleteView(BasicActionView):
    def post(self, request, pk):
        obj = get_object_or_404(MeuModel, pk=pk, usuario=request.user)
        obj.business.excluir()
        return self.json_success("Registro excluído com sucesso.")
```

### 8. `admin.py` — somente superusuários

```python
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from Financeiro.lancamentos.admin import SuperuserOnlyMixin
from .models import MeuModel

@admin.register(MeuModel)
class MeuModelAdmin(SuperuserOnlyMixin, SimpleHistoryAdmin):
    list_display = ["__str__", "usuario", "created_at"]
    search_fields = ["usuario__username"]
    readonly_fields = ["created_at", "updated_at"]
```

### 9. `settings.py` — registrar o app

```python
INSTALLED_APPS = [
    # ...apps existentes...
    "NovoDominio.novoapp",
]
```

### 10. `hackathon/urls.py` — incluir as rotas

```python
path("novodominio/", include("NovoDominio.novoapp.urls")),
```

### 11. Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py check
```

## Commits sugeridos

```
feat(novodominio): criar model MeuModel com BasicModel e mixins
feat(novodominio): implementar business, rules e helpers
feat(novodominio): adicionar views CRUD e templates
feat(novodominio): registrar admin restrito a superusuários
test(novodominio): adicionar testes das views
docs(novodominio): criar instructions do módulo
```
