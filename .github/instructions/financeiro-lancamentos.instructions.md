---
applyTo: "Financeiro/**"
---

# Instructions — Módulo `Financeiro/lancamentos`

## Propósito

Módulo central do sistema. Gerencia categorias financeiras e lançamentos 
(receitas e despesas) de cada usuário, com dashboard, relatórios e exportação PDF.

## Models

### `Categoria`
- Herda: `BasicModel`, `BusinessModelMixin`, `HelperModelMixin`, `RulesModelMixin`
- Campos: `nome` (único por usuário), `descricao`, `cor` (hex), `usuario` (FK)
- Restrição: `unique_together = [("nome", "usuario")]`
- `related_name` de lançamentos: `lancamentos`

### `Lancamento`
- Herda: `BasicModel`, `BusinessModelMixin`, `HelperModelMixin`, `RulesModelMixin`
- Campos: `tipo` (receita/despesa), `descricao`, `valor` (Decimal 12,2), `data`, `categoria` (FK PROTECT), `usuario` (FK), `observacao`
- Constantes: `Lancamento.TIPO_RECEITA = "receita"`, `Lancamento.TIPO_DESPESA = "despesa"`

## Camadas

### Business (`business.py`)
- `CategoriaBusiness(ModelBusiness)` — `criar()`, `atualizar()`, `excluir()` (bloqueia se tem lançamentos)
- `LancamentoBusiness(ModelBusiness)` — `criar()`, `atualizar()`, `excluir()`
- Todas as operações de escrita em `transaction.atomic()`

### Rules (`rules.py`)
- `CategoriaRules(ModelRules)` — `validar_nome_unico()`
- `LancamentoRules(ModelRules)` — `validar_valor()`, `validar_categoria_do_usuario()`

### Helper (`helpers.py`)
- `CategoriaHelper(ModelHelper)` — `listar_por_usuario(usuario)`
- `LancamentoHelper(ModelHelper)` — `listar_por_usuario(usuario, filtros=None)`, `calcular_saldo_usuario(usuario)`, `calcular_saldo_usuario_qs(qs)`, `ultimos_lancamentos(usuario, n=5)`, `totais_por_mes(usuario, ano=None)`, `totais_por_categoria(usuario, tipo=None)`

## Views

| View | Herda | Rota |
|---|---|---|
| `DashboardView` | `BasicTemplateView` | `GET /financeiro/` |
| `LancamentoListView` | `BasicTableView` | `GET /financeiro/lancamentos/` |
| `LancamentoCreateView` | `BasicCreateView` | `GET/POST /financeiro/lancamentos/novo/` |
| `LancamentoUpdateView` | `BasicUpdateView` | `GET/POST /financeiro/lancamentos/<pk>/editar/` |
| `LancamentoDeleteView` | `BasicActionView` | `POST /financeiro/lancamentos/<pk>/excluir/` |
| `CategoriaListView` | `BasicTableView` | `GET /financeiro/categorias/` |
| `CategoriaCreateView` | `BasicCreateView` | `GET/POST /financeiro/categorias/nova/` |
| `CategoriaUpdateView` | `BasicUpdateView` | `GET/POST /financeiro/categorias/<pk>/editar/` |
| `CategoriaDeleteView` | `BasicActionView` | `POST /financeiro/categorias/<pk>/excluir/` |
| `RelatorioView` | `BasicTemplateView` | `GET /financeiro/relatorio/` |
| `RelatorioPDFView` | `BasicTemplateView` | `GET /financeiro/relatorio/pdf/` |

## Templates

```
Financeiro/lancamentos/templates/financeiro/lancamentos/
  dashboard.html
  lancamento_lista.html
  lancamento_form.html        ← compartilhado: criar e editar
  categoria_lista.html
  categoria_form.html         ← compartilhado: criar e editar
  relatorio.html
  relatorio_pdf.html          ← CSS inline only (xhtml2pdf)
  partials/
    cards_saldo.html
    lancamento_tabela.html
    categoria_tabela.html
```

## Regras críticas

- **Todo queryset deve filtrar por `usuario=self.request.user`** — nunca exibir dados de outro usuário.
- Categoria não pode ser excluída se tiver lançamentos vinculados (`lancamentos.exists()`).
- O `related_name` entre `Lancamento` e `Categoria` é `lancamentos` (não `lancamento_set`).
- O PDF usa `xhtml2pdf` — o template `relatorio_pdf.html` deve usar **apenas CSS inline**.
- A listagem de lançamentos suporta AJAX via `HTTP_X_REQUESTED_WITH: XMLHttpRequest` e retorna o partial `lancamento_tabela.html`.

## Admin (`admin.py`)

```python
class SuperuserOnlyMixin:
    def has_module_perms(self, request, app_label=None):
        return request.user.is_active and request.user.is_superuser
    # has_permission, has_view_permission, has_add_permission,
    # has_change_permission, has_delete_permission — mesma lógica

@admin.register(Categoria)
class CategoriaAdmin(SuperuserOnlyMixin, SimpleHistoryAdmin): ...

@admin.register(Lancamento)
class LancamentoAdmin(SuperuserOnlyMixin, SimpleHistoryAdmin): ...
```

## Seed de dados (`management/commands/seed_demo.py`)

```bash
python manage.py seed_demo
```

Cria dois usuários idempotentemente:
- `demo1` / `demo2` (senha: `demo1234`)
- 10 categorias por usuário
- ~45 lançamentos por usuário (15 tipos × 3 meses)

## Testes (`tests.py`)

41 testes cobrindo:
- Redirecionamento sem login
- Dashboard (acesso, context, templates)
- Lançamentos: CRUD, AJAX, filtros, isolamento
- Categorias: CRUD, AJAX, constraint lançamentos vinculados, isolamento
- Relatório: acesso, filtros, isolamento
- Relatório PDF: status 200, content-type

```bash
python manage.py test Financeiro.lancamentos --verbosity=2
```

## Padrões de queryset

```python
# CORRETO — sempre com select_related e filtro por usuário
Lancamento.objects.filter(usuario=self.request.user)\
    .select_related("categoria", "usuario")\
    .order_by("-data")

# ERRADO — nunca sem filtro de usuário
Lancamento.objects.all()
```

## Filtros disponíveis no Relatório / Lista

| Parâmetro GET | Tipo | Descrição |
|---|---|---|
| `tipo` | `"receita"` / `"despesa"` | Filtra por tipo de lançamento |
| `categoria` | `int` (pk) | Filtra por categoria |
| `data_inicio` | `YYYY-MM-DD` | Data inicial do período |
| `data_fim` | `YYYY-MM-DD` | Data final do período |
| `busca` | `str` | Busca textual na descrição |
