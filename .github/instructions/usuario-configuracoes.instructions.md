---
applyTo: "Usuario/configuracoes/**"
---

# Instructions — `Usuario/configuracoes`

## Visão Geral

App responsável pelas preferências do usuário, em especial a **moeda de exibição**.

- Valores financeiros são **sempre armazenados em BRL** no banco de dados.
- A conversão para a moeda preferida é feita **em tempo real de exibição** via template filter.
- A infraestrutura de cotações fica em `common/currency_service.py`.

---

## Model: `PreferenciaUsuario`

- Herda `BasicModel` + `BusinessModelMixin` + `HelperModelMixin` + `RulesModelMixin`
- `usuario`: `OneToOneField(User, related_name="preferencia")`
- `moeda_preferida`: `CharField(max_length=10, default="BRL")` — código ISO
- Classes injetadas em `ConfiguracoesConfig.ready()`

---

## Fluxo de Cotações (`common/currency_service.py`)

```
obter_cotacoes()
  → lê data/cotacoes.json (cache)
  → se expirado (>1 min) ou inexistente: chama AwesomeAPI e reescreve o arquivo
  → retorna None se API e cache falharem
```

Funções públicas:
- `obter_cotacoes()` → dict completo do cache
- `obter_moedas_disponiveis()` → `{codigo: nome}` de moedas X-BRL disponíveis
- `obter_taxa_para_moeda(codigo)` → float (1/bid); para BRL retorna 1.0
- `converter_valor(valor_brl, codigo)` → Decimal convertido
- `obter_simbolo_moeda(codigo)` → str do símbolo (ex: "US$", "€")

---

## Context Processor: `common/context_processors.moeda_context`

Injeta `moeda_usuario` em **todos os templates** autenticados:

```python
{
    "codigo": "USD",
    "simbolo": "US$",
    "taxa": 0.1957,         # float — valor_moeda = valor_brl * taxa
    "taxa_inversa": 5.11,   # float — quantos BRL = 1 moeda (= bid)
    "nome": "Dólar Americano",
}
```

Para BRL: `taxa = 1.0`, `taxa_inversa = 1.0`, `simbolo = "R$"`.
Em caso de falha, retorna BRL como fallback seguro.

---

## Template Filter: `converter_moeda`

Registrado como builtin — disponível em **todos** os templates sem `{% load %}`.

```html
{{ saldo.receitas|converter_moeda:moeda_usuario.taxa }}
```

Retorna `Decimal` com 2 casas decimais. Em caso de erro, retorna o valor original.

---

## Camadas

### Business: `PreferenciaUsuarioBusiness`
- `atualizar_moeda()` — valida e salva dentro de `transaction.atomic()`

### Rules: `PreferenciaUsuarioRules`
- `validar_moeda_disponivel()`:
  - BRL sempre aceito
  - Outros códigos validados contra a API/cache
  - Se API indisponível, aceita qualquer código (não bloqueia usuário)

### Helper: `PreferenciaUsuarioHelper`
- `obter_preferencia(usuario)` — `get_or_create` com default BRL; nunca retorna None

---

## View: `ConfiguracaoMoedaView`

```
GET  /configuracoes/moeda/  → exibe form com moedas disponíveis da API
POST /configuracoes/moeda/  → salva preferência via business
```

Override de `get_object()` usa `PreferenciaUsuarioHelper.obter_preferencia()`.

---

## Regras de Negócio

- BRL é a moeda base e sempre válida
- A conversão é **somente de exibição** — nunca afeta os dados armazenados
- Se a AwesomeAPI estiver indisponível, o sistema exibe os valores em BRL (fallback)
- O cache TTL é de 60 segundos; o arquivo é `data/cotacoes.json` (não versionado no git)

---

## Proibições e Obrigações

- **NUNCA** use type hints em nenhum arquivo Python
- **NUNCA** converta valores antes de salvar no banco — sempre BRL
- **SEMPRE** use o helper `obter_preferencia()` para acessar a preferência (evita null)
- **SEMPRE** trate falhas da API com try/except (API pode estar indisponível)
- **NUNCA** acesse a preferência de outro usuário — o context processor usa `request.user`

---

## Adicionar Nova Preferência ao Model

1. Adicionar campo ao `PreferenciaUsuario` em `models.py`
2. Adicionar ao form `PreferenciaUsuarioForm` em `forms.py`
3. Criar `validar_<campo>()` em `PreferenciaUsuarioRules`
4. Chamar a rule em `PreferenciaUsuarioBusiness.atualizar_moeda()` (ou criar novo método)
5. Rodar `makemigrations configuracoes` e `migrate`

---

## Convenção de Commits

```
feat(configuracoes): <descrição>
fix(configuracoes): <descrição>
test(configuracoes): <descrição>
```
