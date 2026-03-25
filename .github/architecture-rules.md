# Architecture Rules (AI Reference)

Referência técnica para IAs gerarem código compatível com a arquitetura deste projeto Django.

---

## Arquitetura em Camadas

```
View → Business → Rules
           ↓        ↓
        Helper    Helper
```

| Camada   | Arquivo       | Faz                                                    | Não faz                                      |
|----------|---------------|--------------------------------------------------------|----------------------------------------------|
| View     | `views.py`    | Recebe request, chama Business/Helper, retorna response | Lógica de negócio, queries complexas         |
| Business | `business.py` | Orquestra fluxo, persiste dados, chama Rules/Helper    | Acessar request, retornar HTTP               |
| Rules    | `rules.py`    | Valida regras de negócio                               | Persistir dados, fazer queries de listagem   |
| Helper   | `helpers.py`  | Queries reutilizáveis read-only                        | Gravar dados, lançar exceções de negócio     |
| Model    | `models.py`   | Define campos, herda `BasicModel` + mixins             | Conter business logic, fazer imports de views |

---

## Regras Obrigatórias

### Python
- **NUNCA** use type hints (`: str`, `: int`, `->`, etc.) em nenhum arquivo `.py`.

### Models
- Todo Model herda `BasicModel` + `BusinessModelMixin` + `HelperModelMixin` + `RulesModelMixin`.
- Declare `business_class = None`, `helper_class = None`, `rules_class = None` no Model.
- As classes reais são injetadas em `AppConfig.ready()`.

### Views
- Toda View herda de uma `BasicView` de `core.views` (`BasicTableView`, `BasicCreateView`, `BasicUpdateView`, `BasicDeleteView`, `BasicActionView`, `BasicTemplateView`, `BasicDetailView`).
- Toda View de dados filtra por `usuario=request.user` — **sem exceção**.
- View chama `Business` para escrita e `Helper` para leitura.
- Queries com FK usam `select_related` / `prefetch_related`.

### Business
- Herda `ModelBusiness` (`core.mixins`).
- Todo método de escrita está dentro de `transaction.atomic()`.
- Exceções tratadas com o padrão obrigatório (ver abaixo).
- Chama `Rules` antes de `save()`.
- Nunca instanciar manualmente ou criar métodos estáticos.

### Rules
- Herda `ModelRules` (`core.mixins`).
- Retorna `False` quando a regra é atendida.
- Lança `BusinessRulesExceptions` quando a regra é violada.
- **Nunca** persiste dados.
- Nunca instanciar manualmente ou criar métodos estáticos.

### Helper
- Herda `ModelHelper` (`core.mixins`).
- Contém apenas métodos `@staticmethod` de leitura.
- **Nunca** grava dados nem lança exceções de negócio.
- Nunca instanciar manualmente ou criar métodos estáticos.

### Exceções — Padrão Obrigatório no Business

```python
def criar(self):
    try:
        with transaction.atomic():
            self.model_instance.rules.validar_algo()
            self.model_instance.save()
            return self.model_instance
    except (BusinessRulesExceptions, ProcessException):
        raise
    except Exception as exc:
        raise SystemErrorException("Mensagem amigável.") from exc
```

| Exceção                   | Lançada por  | HTTP |
|---------------------------|-------------|------|
| `BusinessRulesExceptions` | Rules       | 400  |
| `ProcessException`        | Business    | 400  |
| `SystemErrorException`    | Business    | 500  |

### Injeção via `AppConfig.ready()`

```python
class MeuAppConfig(AppConfig):
    def ready(self):
        from .models import MeuModel
        from .business import MeuBusiness
        from .helpers import MeuHelper
        from .rules import MeuRules

        MeuModel.business_class = MeuBusiness
        MeuModel.helper_class = MeuHelper
        MeuModel.rules_class = MeuRules
```

---

## Quando criar cada camada

### Criar um Business quando:
- Há operação de **escrita** (criar, atualizar, excluir).
- Há orquestração entre múltiplas Rules ou múltiplos Models.

### Criar uma Rule quando:
- Existe validação de **regra de negócio** (valor > 0, nome único, pertence ao usuário, etc.).
- A validação **não** é mera checagem de formulário (campo obrigatório, formato de e-mail).

### Criar um Helper quando:
- Existe query de **leitura** reutilizável (listagem filtrada, cálculos agregados, dashboards).
- A query é usada em mais de uma View ou contexto.

---

## Anti-patterns — O que NÃO fazer

### 1. Lógica de negócio na View

```python
# ❌ ERRADO
class MeuCreateView(BasicCreateView):
    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.valor <= 0:                     # regra de negócio na view
            raise BusinessRulesExceptions(...)
        obj.save()
```

```python
# ✅ CORRETO
class MeuCreateView(BasicCreateView):
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.usuario = self.request.user
        obj.business.criar()                   # delega ao business
        messages.success(self.request, MSG_CRIADO_SUCESSO)
        return redirect(self.success_url)
```

### 2. Business sem `transaction.atomic()`

```python
# ❌ ERRADO
def criar(self):
    self.model_instance.rules.validar_valor()
    self.model_instance.save()
```

```python
# ✅ CORRETO
def criar(self):
    try:
        with transaction.atomic():
            self.model_instance.rules.validar_valor()
            self.model_instance.save()
    except (BusinessRulesExceptions, ProcessException):
        raise
    except Exception as exc:
        raise SystemErrorException("Erro ao criar.") from exc
```

### 3. Queryset sem filtro de usuário

```python
# ❌ ERRADO — expõe dados de outros usuários
def get_queryset(self):
    return Lancamento.objects.all()
```

```python
# ✅ CORRETO
def get_queryset(self):
    return Lancamento.objects.filter(usuario=self.request.user)
```

### 4. Type hints em código Python

```python
# ❌ ERRADO
def calcular_saldo(self, usuario: User) -> dict:
    ...
```

```python
# ✅ CORRETO
def calcular_saldo(self, usuario):
    ...
```

### 5. Helper que grava dados

```python
# ❌ ERRADO — Helper deve ser read-only
class MeuHelper(ModelHelper):
    @staticmethod
    def criar_padrao(usuario):
        return MeuModel.objects.create(usuario=usuario, nome="Padrão")
```

```python
# ✅ CORRETO — gravação fica no Business
class MeuBusiness(ModelBusiness):
    def criar_padrao(self):
        with transaction.atomic():
            self.model_instance.save()
```

### 6. Rules que persiste dados

```python
# ❌ ERRADO
class MinhaRules(ModelRules):
    def validar_e_salvar(self):
        if self.model_instance.valor <= 0:
            raise BusinessRulesExceptions("Valor inválido.")
        self.model_instance.save()             # Rules NÃO salva
```

```python
# ✅ CORRETO
class MinhaRules(ModelRules):
    def validar_valor(self):
        if self.model_instance.valor <= 0:
            raise BusinessRulesExceptions("Valor inválido.")
        return False
```

### 7. Import direto no Model (circular)

```python
# ❌ ERRADO — causa import circular
from .business import MeuBusiness

class MeuModel(BasicModel, BusinessModelMixin):
    business_class = MeuBusiness
```

```python
# ✅ CORRETO — injeção no AppConfig.ready()
class MeuModel(BasicModel, BusinessModelMixin):
    business_class = None      # injetado em ready()
```

### 8. Engolir exceções conhecidas

```python
# ❌ ERRADO — perde a exceção de regra
except Exception as exc:
    raise SystemErrorException("Erro.") from exc
```

```python
# ✅ CORRETO — relança antes do catch genérico
except (BusinessRulesExceptions, ProcessException):
    raise
except Exception as exc:
    raise SystemErrorException("Erro.") from exc
```

---

## Checklist rápido para novos módulos

- [ ] Model herda `BasicModel` + 3 mixins
- [ ] `business_class`, `helper_class`, `rules_class` = `None`
- [ ] `AppConfig.ready()` injeta as classes
- [ ] Business usa `transaction.atomic()` + padrão de exceções
- [ ] Rules retorna `False` ou lança `BusinessRulesExceptions`
- [ ] Helper é read-only, métodos `@staticmethod`
- [ ] Views herdam de `BasicView` do `core.views`
- [ ] Todo queryset filtra por `usuario=request.user`
- [ ] Nenhum type hint em arquivos Python
- [ ] Strings de UI centralizadas em `common/constants.py`
