# Gestão Financeira Pessoal

Sistema web para controle de finanças pessoais, desenvolvido em Django com arquitetura em camadas como parte do Hackathon **Ctrl+Alt+AI: Hackeando a Rotina de Programação** (M2A / IntGest).

---

## Sumário

- [Objetivo](#objetivo)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Arquitetura](#arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Como Executar](#como-executar)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Rotas Principais](#rotas-principais)
- [Testes](#testes)
- [Comandos Úteis](#comandos-úteis)
- [Usuários de Demonstração](#usuários-de-demonstração)
- [Diagramas](docs/diagramas.md)

---

## Objetivo

Prova de Conceito de um mini software de **Gestão Financeira Pessoal** que permite:

- Registrar receitas e despesas com categorias.
- Visualizar saldo atualizado automaticamente.
- Ver um dashboard com resumo financeiro e gráficos.
- Gerenciar lançamentos (criar, editar, excluir) com dados isolados por usuário.
- Exportar relatórios filtrados em PDF.

---

## Funcionalidades

| # | Funcionalidade | Descrição |
|---|---|---|
| 1 | Cadastro de receitas | Crie entradas financeiras com categoria, data e valor |
| 2 | Cadastro de despesas | Crie saídas financeiras com categoria, data e valor |
| 3 | Categorias personalizadas | Crie, edite e exclua categorias com cor e nome únicos por usuário |
| 4 | Listagem com filtros | Filtre lançamentos por tipo, categoria, período e busca textual |
| 5 | Saldo automático | Receitas − Despesas calculadas em tempo real |
| 6 | Dashboard com gráficos | Gráfico de barras mensal e gráfico de rosca por categoria |
| 7 | Relatório com exportação PDF | Relatório filtrado exportável via xhtml2pdf |
| 8 | Isolamento por usuário | Cada usuário vê somente seus próprios dados |
| 9 | Admin restrito a superusuários | Painel Django Admin disponível apenas para `is_superuser=True` |
| 10 | Histórico de alterações | django-simple-history registra todo histórico de edições |

---

## Stack

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.x | Linguagem principal |
| Django | 6.0.3 | Framework web |
| SQLite | — | Banco de dados local |
| django-simple-history | 3.11.0 | Histórico de alterações nos models |
| python-decouple | 3.8 | Gerenciamento de variáveis de ambiente |
| xhtml2pdf | 0.2.17 | Exportação de relatórios em PDF |
| Bootstrap | 5 CDN | Interface responsiva |
| Chart.js | 4.4.0 CDN | Gráficos no dashboard |

---

## Arquitetura

O projeto segue uma **arquitetura em camadas por domínio**:

```
Domínio (ex: Financeiro)/
  app (ex: lancamentos)/
    models.py       ← Herda BasicModel + mixins de composição
    views.py        ← Herda BasicView; SÓ lida com request/response
    business.py     ← Processamento, regras e tratamento de erros
    helpers.py      ← Queries reutilizáveis, funções auxiliares sem escrita
    rules.py        ← Regras de negócio; retorna False ou lança exceção
    forms.py
    urls.py
    admin.py
    tests.py
```

### Camadas

| Camada | Responsabilidade |
|---|---|
| **View** | Recebe request, chama Business, retorna response. Sem regra de negócio. |
| **Business** | Orquestra o fluxo, processa dados, chama Rules e Helper. |
| **Rules** | Valida regras de negócio. Lança `BusinessRulesExceptions` ou retorna `False`. |
| **Helper** | Queries complexas reutilizáveis e funções auxiliares (sem escrita). |

### Exceções

| Exceção | Lançada por | HTTP |
|---|---|---|
| `BusinessRulesExceptions` | Rules | 400 |
| `ProcessException` | Business (erro tratado) | 400 |
| `SystemErrorException` | Business (erro inesperado) | 500 |

---

## Estrutura de Pastas

```
hackathon/           ← Configurações do projeto Django
core/                ← Classes base, exceções, mixins, constantes técnicas
common/              ← Constantes de texto, widgets personalizados
Financeiro/          ← Domínio financeiro (app: lancamentos)
Usuario/             ← Domínio de usuário (app: autenticacao)
templates/           ← Templates HTML organizados por app
  base.html          ← Layout raiz (público: login, landing)
  base_auth.html     ← Layout autenticado com sidebar (extends base.html)
  core/              ← Páginas de erro (400, 403, 404, 500)
static/              ← Assets estáticos (CSS, JS, imagens)
manage.py
requirements.txt
.env-example
```

---

## Como Executar

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd hackathon
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env-example .env
# Edite o .env com sua SECRET_KEY e demais configurações
```

### 5. Executar as migrações

```bash
python manage.py migrate
```

### 6. Criar um superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 7. Popular dados de demonstração (opcional)

```bash
python manage.py seed_demo
```

### 8. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Variáveis de Ambiente

Copie `.env-example` para `.env` e preencha:

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave secreta do Django | — (obrigatório) |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por vírgula) | `127.0.0.1,localhost` |

---

## Comandos Úteis

```bash
# Rodar servidor de desenvolvimento
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Popular dados de demonstração
python manage.py seed_demo

# Rodar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic

# Verificar saúde do projeto
python manage.py check
```

---

## Testes

```bash
# Rodar todos os testes
python manage.py test

# Rodar testes do módulo financeiro com saída detalhada
python manage.py test Financeiro.lancamentos --verbosity=2
```

A suite de testes cobre:

- Autenticação: redirecionamento para login em rotas protegidas
- `DashboardView`: acesso, template, context (saldo, gráfico, últimos)
- `LancamentoListView`: listagem, filtros, AJAX partial, isolamento de dados
- `LancamentoCreateView` / `UpdateView`: GET/POST, redirecionamento, isolamento
- `LancamentoDeleteView`: resposta JSON, isolamento
- `CategoriaListView` / `CreateView` / `UpdateView`: CRUD completo
- `CategoriaDeleteView`: exclusão com e sem lançamentos vinculados, isolamento
- `RelatorioView`: acesso, filtros, isolamento
- `RelatorioPDFView`: status 200, `Content-Type: application/pdf`

---

## Rotas Principais

| Método | URL | Nome | Descrição |
|---|---|---|---|
| GET | `/` | `landing` | Landing page pública |
| GET/POST | `/login/` | `usuario:login` | Login |
| POST | `/logout/` | `usuario:logout` | Logout |
| GET | `/financeiro/` | `financeiro:dashboard` | Dashboard |
| GET | `/financeiro/lancamentos/` | `financeiro:lancamento-lista` | Lista de lançamentos |
| GET/POST | `/financeiro/lancamentos/novo/` | `financeiro:lancamento-criar` | Criar lançamento |
| GET/POST | `/financeiro/lancamentos/<pk>/editar/` | `financeiro:lancamento-editar` | Editar lançamento |
| POST | `/financeiro/lancamentos/<pk>/excluir/` | `financeiro:lancamento-excluir` | Excluir (AJAX) |
| GET | `/financeiro/categorias/` | `financeiro:categoria-lista` | Lista de categorias |
| GET/POST | `/financeiro/categorias/nova/` | `financeiro:categoria-criar` | Criar categoria |
| GET/POST | `/financeiro/categorias/<pk>/editar/` | `financeiro:categoria-editar` | Editar categoria |
| POST | `/financeiro/categorias/<pk>/excluir/` | `financeiro:categoria-excluir` | Excluir (AJAX) |
| GET | `/financeiro/relatorio/` | `financeiro:relatorio` | Relatório com filtros |
| GET | `/financeiro/relatorio/pdf/` | `financeiro:relatorio-pdf` | Download PDF |
| GET | `/admin/` | — | Django Admin (superusuários) |

---

## Usuários de Demonstração

Após executar `python manage.py seed_demo`, os seguintes usuários ficam disponíveis:

| Usuário | Senha | Descrição |
|---|---|---|
| `demo1` | `demo1234` | Usuário A com 10 categorias e ~45 lançamentos |
| `demo2` | `demo1234` | Usuário B com 10 categorias e ~45 lançamentos |

Os dados são completamente isolados entre os dois usuários.

---
