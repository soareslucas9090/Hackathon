---
name: create-feature-following-project-architecture
description: |
  Skill de planejamento arquitetural para novas funcionalidades.
  USE PARA: qualquer pedido de nova feature, endpoint, tela ou comportamento.
  OBRIGA a IA a montar um plano de arquitetura ANTES de gerar qualquer código,
  identificando app, models, camadas necessárias e delegando a implementação
  para as skills específicas de cada módulo.
---

# SKILL — Planejar Feature Seguindo a Arquitetura do Projeto

## Regra principal

**NUNCA gere código diretamente.** Antes de qualquer implementação, execute o plano abaixo e apresente a saída formatada ao usuário para validação.

---

## Passo 1 — Identificar o App alvo

Leia a estrutura do projeto e determine:

| Pergunta | Como decidir |
|----------|-------------|
| A feature pertence a um domínio existente? | Verifique as pastas de domínio (`Financeiro/`, `Usuario/`, etc.) e suas instructions em `.github/instructions/`. |
| É necessário criar um novo domínio/app? | Se sim, delegue para a skill `novo-modulo`. |

**Saída esperada:**
```
App alvo: Financeiro/lancamentos
Justificativa: <uma linha>
```

Se a feature envolve **mais de um app**, liste todos e indique qual é o principal.

---

## Passo 2 — Identificar Models afetados

Para cada Model envolvido, determine:

| Ação | Critério |
|------|----------|
| Criar Model novo | Não existe Model que represente a entidade pedida. |
| Alterar Model existente | Precisa de campo novo, index novo ou alteração de constraint. |
| Nenhuma alteração | Os Models existentes já cobrem os dados necessários. |

**Saída esperada:**
```
Models:
  - Lancamento (existente, sem alteração)
  - MetaPoupanca (novo) — campos: nome, valor_alvo, valor_atual, prazo, usuario FK
```

Lembre-se:
- Todo Model novo herda `BasicModel` + `BusinessModelMixin` + `HelperModelMixin` + `RulesModelMixin`.
- Declare `business_class = None`, `helper_class = None`, `rules_class = None`.
- Todo Model tem `usuario` FK com filtro obrigatório.
- **NUNCA** use type hints.

---

## Passo 3 — Decidir camadas necessárias

Para cada Model afetado, avalie:

### Business novo?

| Sim | Não |
|-----|-----|
| Há operação de escrita (criar, atualizar, excluir) | A feature é apenas leitura/exibição |
| Há orquestração entre Rules + persistência | O Business existente já cobre a operação |

### Rules novas?

| Sim | Não |
|-----|-----|
| Existe validação de regra de negócio (valor > 0, unicidade, pertencimento de FK) | A validação é de formulário (campo obrigatório, formato) |
| A regra não existe em nenhuma Rules atual do Model | A Rules existente já cobre |

### Helper novo?

| Sim | Não |
|-----|-----|
| Existe query de leitura reutilizável (listagem, agregação, dashboard) | A query é trivial e usada em uma única View |
| A query será usada em mais de uma View ou contexto | O Helper existente já tem o método |

### View nova?

| Sim | Não |
|-----|-----|
| A feature precisa de rota/endpoint novo | A feature pode ser adicionada a uma View existente (ex.: novo campo no context) |

### Form novo?

| Sim | Não |
|-----|-----|
| A feature envolve input do usuário com Model novo ou campos novos | A feature é apenas leitura |
| O Form existente não cobre os campos necessários | O Form existente já serve |

**Saída esperada:**
```
Camadas necessárias:
  MetaPoupanca:
    - Business: CRIAR (criar, atualizar, excluir)
    - Rules: CRIAR (validar_valor_alvo, validar_prazo_futuro)
    - Helper: CRIAR (listar_por_usuario, calcular_progresso)
    - Views: CRIAR (List, Create, Update, Delete)
    - Form: CRIAR (MetaPoupancaForm)
  Lancamento:
    - Business: SEM ALTERAÇÃO
    - Rules: SEM ALTERAÇÃO
    - Helper: ADICIONAR método totais_por_meta(usuario)
    - Views: SEM ALTERAÇÃO
    - Form: SEM ALTERAÇÃO
```

---

## Passo 4 — Montar o Plano de Implementação

Organize as tarefas na ordem correta de dependência:

```
Plano de Implementação:
  1. [Model]    Criar MetaPoupanca em Financeiro/lancamentos/models.py
  2. [Apps]     Registrar classes em LancamentosConfig.ready()
  3. [Business] Criar MetaPoupancaBusiness em business.py
  4. [Rules]    Criar MetaPoupancaRules em rules.py
  5. [Helper]   Criar MetaPoupancaHelper em helpers.py
  6. [Helper]   Adicionar totais_por_meta() em LancamentoHelper
  7. [Form]     Criar MetaPoupancaForm em forms.py
  8. [Views]    Criar views CRUD em views.py
  9. [URLs]     Registrar rotas em urls.py
  10. [Template] Criar templates lista + form + partials
  11. [Admin]   Registrar MetaPoupancaAdmin em admin.py
  12. [Test]    Criar testes das views
  13. [Migration] makemigrations + migrate
```

---

## Passo 5 — Delegar para skills específicas

Após validação do plano pelo usuário, delegue a implementação:

| Situação | Skill a invocar |
|----------|-----------------|
| Novo módulo/domínio | `novo-modulo` |
| Alteração em `Financeiro/lancamentos` | `financeiro-lancamentos` |
| Criação/alteração de testes | `testes` |

Ao delegar, **passe todo o contexto** para a skill:
- Nome do Model, campos, relacionamentos
- Métodos de Business/Rules/Helper a criar
- Views e rotas planejadas
- Regras de negócio identificadas

---

## Formato de saída completo

Apresente ao usuário neste formato antes de implementar:

```markdown
## Plano de Arquitetura — [Nome da Feature]

**App alvo:** Financeiro/lancamentos
**Justificativa:** <uma linha>

### Models
- <lista>

### Camadas
- <tabela de decisão>

### Plano de Implementação
1. <passo ordenado>
2. ...

### Skills delegadas
- <skill>: <o que será feito>

### Commits sugeridos
- feat(modulo): <descrição>
- test(modulo): <descrição>
```

---

## Regras absolutas desta skill

1. **NUNCA** pule o planejamento — mesmo para features "simples".
2. **NUNCA** gere código sem apresentar o plano primeiro.
3. **NUNCA** crie arquivo em camada errada (ex.: query de leitura no Business).
4. **NUNCA** use type hints em nenhum arquivo Python.
5. **SEMPRE** verifique se já existe Business/Rules/Helper antes de criar novo.
6. **SEMPRE** filtre por `usuario=request.user` em toda query.
7. **SEMPRE** siga o padrão de exceções do Business (`try/atomic/except`).
8. **SEMPRE** delegue implementação para a skill do módulo correspondente.
