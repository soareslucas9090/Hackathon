---
name: financeiro-lancamentos
description: |
  Skill para trabalhar com o módulo Financeiro/lancamentos.
  USE PARA: adicionar ou modificar lançamentos, categorias, filtros, helpers,
  regras de negócio, relatórios, dashboard e exportação PDF.
  Contém padrões de queryset, business, rules, helper e templates deste módulo.
---

# SKILL — Módulo Financeiro (lancamentos)

## Quando usar esta skill

Use sempre que for necessário:
- Adicionar ou modificar lançamentos ou categorias
- Criar novos filtros, helpers ou regras financeiras
- Adicionar novas views ao módulo Financeiro
- Expandir os relatórios ou o dashboard

## Estado atual do módulo

### Models
- `Categoria`: nome (único por usuário), descricao, cor (#hex), usuario FK
- `Lancamento`: tipo (receita/despesa), descricao, valor (Decimal), data, categoria FK (PROTECT), usuario FK

### Helpers disponíveis (LancamentoHelper)
- `listar_por_usuario(usuario, filtros=None)` — lista com filtros opcionais
- `calcular_saldo_usuario(usuario)` — retorna dict com receitas/despesas/saldo
- `calcular_saldo_usuario_qs(qs)` — calcula saldo de um queryset filtrado
- `ultimos_lancamentos(usuario, n=5)` — últimos N lançamentos
- `totais_por_mes(usuario, ano=None)` — agrupado por mês para gráficos
- `totais_por_categoria(usuario, tipo=None)` — agrupado por categoria

### Helpers disponíveis (CategoriaHelper)
- `listar_por_usuario(usuario)` — lista ordenada por nome

### Business disponíveis
- `CategoriaBusiness`: `criar()`, `atualizar()`, `excluir()` (bloqueia se tem lançamentos)
- `LancamentoBusiness`: `criar()`, `atualizar()`, `excluir()`

### Rules disponíveis
- `CategoriaRules`: `validar_nome_unico()`
- `LancamentoRules`: `validar_valor()`, `validar_categoria_do_usuario()`

## Como adicionar um novo filtro ao relatório

1. Adicione o parâmetro GET em `RelatorioView.get_context_data` (ou `get_queryset`).
2. Aplique o filtro ao queryset `filtros = {...}`.
3. Passe o filtro para `LancamentoHelper.listar_por_usuario(usuario, filtros=filtros)`.
4. Atualize o template `relatorio.html` com o novo campo do formulário.
5. Atualize os testes em `RelatorioViewTest`.

## Como adicionar um novo gráfico ao dashboard

1. Crie um novo helper em `LancamentoHelper` que retorna os dados serializáveis.
2. Em `DashboardView.get_context_data`, adicione o resultado ao contexto.
3. No template `dashboard.html`, instancie um novo `<canvas>` e inicialize o Chart.js.
4. Os dados do contexto devem ser serializados com `json.dumps()` usando `DjangoJSONEncoder`.

## Regras críticas

- O `related_name` de `Lancamento` para `Categoria` é **`lancamentos`** (não `lancamento_set`).
- Ao excluir categoria, verificar com `self.model_instance.lancamentos.exists()`.
- O `valor` do lançamento deve ser `> 0` — validado em `LancamentoRules.validar_valor()`.
- A categoria usada no lançamento deve pertencer ao mesmo usuário — validado em `validar_categoria_do_usuario()`.
- O PDF usa `xhtml2pdf.pisa` — **apenas CSS inline** no template `relatorio_pdf.html`.
- Toda resposta AJAX de exclusão retorna `{"success": true/false}`.

## Padrão para nova View de ação AJAX

```python
class NovaAcaoView(BasicActionView):
    def post(self, request, pk):
        obj = get_object_or_404(Lancamento, pk=pk, usuario=request.user)
        obj.business.nova_acao()
        return self.json_success("Ação executada com sucesso.")
```

## Padrão para nova regra de negócio

```python
# rules.py
class LancamentoRules(ModelRules):
    def validar_nova_regra(self):
        if condicao_invalida:
            raise BusinessRulesExceptions("Mensagem clara para o usuário.")

# business.py — chamar a regra antes do save()
def criar(self):
    try:
        with transaction.atomic():
            self.model_instance.rules.validar_valor()
            self.model_instance.rules.validar_categoria_do_usuario()
            self.model_instance.rules.validar_nova_regra()  # ← nova regra aqui
            self.model_instance.save()
    except (BusinessRulesExceptions, ProcessException):
        raise
    except Exception as exc:
        raise SystemErrorException("Erro inesperado ao criar lançamento.") from exc
```

## Convenção de commits para este módulo

```
feat(financeiro): <descrição>
fix(financeiro): <descrição>
test(financeiro): <descrição>
refactor(financeiro): <descrição>
```
