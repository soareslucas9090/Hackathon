<div align="center">

# 💰 Gestão Financeira Pessoal

**Controle suas finanças de forma simples, clara e segura.**

Desenvolvido em Django com arquitetura em camadas como parte do Hackathon  
**⚡ Ctrl+Alt+AI: Hackeando a Rotina de Programação** — M2A / IntGest

---

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0.3-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/Licen%C3%A7a-MIT-green?style=for-the-badge)

</div>

---

## 📋 Sumário

- [🎯 Objetivo](#-objetivo)
- [✨ Funcionalidades](#-funcionalidades)
- [🧰 Stack e Pacotes](#-stack-e-pacotes)
- [🏗️ Arquitetura](#️-arquitetura)
- [📁 Estrutura de Pastas](#-estrutura-de-pastas)
- [🚀 Como Executar](#-como-executar)
- [⚙️ Variáveis de Ambiente](#️-variáveis-de-ambiente)
- [🛣️ Rotas Principais](#️-rotas-principais)
- [🧪 Testes](#-testes)
- [🔧 Comandos Úteis](#-comandos-úteis)
- [👥 Usuários de Demonstração](#-usuários-de-demonstração)
- [📊 Diagramas](docs/diagramas.md)

---

## 🎯 Objetivo

Uma **Prova de Conceito** de software de Gestão Financeira Pessoal que traz o essencial para quem quer ter controle real sobre o próprio dinheiro — sem complicação, sem excesso.

Com ele você consegue:

- 📥 **Registrar receitas e despesas** organizadas por categorias personalizadas
- 💹 **Visualizar o saldo** atualizado automaticamente em tempo real
- 📊 **Explorar um dashboard** com resumo financeiro e gráficos interativos
- ✏️ **Gerenciar lançamentos** completos: criar, editar e excluir, com dados totalmente isolados por usuário
- 📄 **Exportar relatórios filtrados** diretamente em PDF

---

## ✨ Funcionalidades

| # | Funcionalidade | O que faz |
|:---:|---|---|
| 💵 | **Cadastro de receitas** | Registra entradas financeiras com categoria, data e valor |
| 💸 | **Cadastro de despesas** | Registra saídas financeiras com categoria, data e valor |
| 🏷️ | **Categorias personalizadas** | Crie, edite e exclua categorias com cor e nome únicos por usuário |
| 🔍 | **Listagem com filtros** | Filtre por tipo, categoria, período e busca textual |
| ⚖️ | **Saldo automático** | Receitas − Despesas calculadas em tempo real |
| 📈 | **Dashboard com gráficos** | Gráfico de barras mensal e rosca por categoria via Chart.js |
| 📄 | **Exportação em PDF** | Relatório filtrado exportável (gerado com xhtml2pdf) |
| 🔒 | **Isolamento por usuário** | Cada usuário acessa somente os próprios dados |
| 🛡️ | **Admin restrito** | Painel Django Admin disponível apenas para `is_superuser=True` |
| 🕓 | **Histórico de alterações** | `django-simple-history` registra todo o histórico de edições |

---

## 🧰 Stack e Pacotes

### Backend & Framework

| Pacote | Versão | Para que serve |
|---|:---:|---|
| 🐍 **Python** | 3.x | Linguagem principal do projeto |
| 🎸 **Django** | 6.0.3 | Framework web MVC — views, models, ORM e admin |
| 🗄️ **SQLite** | — | Banco de dados local (sem configuração extra) |
| `asgiref` | 3.11.1 | Suporte ASGI/WSGI para o Django |
| `sqlparse` | 0.5.5 | Formatação de queries SQL (dependência interna do Django) |
| `tzdata` | 2025.3 | Dados de fuso horário para ambientes Windows |

### Funcionalidades e Utilitários

| Pacote | Versão | Para que serve |
|---|:---:|---|
| 📜 **django-simple-history** | 3.11.0 | Registra histórico de todas as alterações nos models |
| 🔑 **python-decouple** | 3.8 | Lê variáveis sensíveis do `.env` (SECRET_KEY, DEBUG…) |
| 🖼️ **Pillow** | 12.1.1 | Processamento de imagens (dependência do xhtml2pdf) |

### Geração de PDF

| Pacote | Versão | Para que serve |
|---|:---:|---|
| 📑 **xhtml2pdf** | 0.2.17 | Converte HTML/CSS em PDF para exportação de relatórios |
| `reportlab` | 4.4.10 | Motor de renderização PDF (base do xhtml2pdf) |
| `pypdf` | 6.9.2 | Manipulação de arquivos PDF já gerados |
| `html5lib` | 1.1 | Parser HTML5 utilizado pelo xhtml2pdf |

### Frontend (via CDN)

| Biblioteca | Versão | Para que serve |
|---|:---:|---|
| 🎨 **Bootstrap** | 5 | Layout responsivo, componentes e utilitários CSS |
| 📊 **Chart.js** | 4.4.0 | Gráficos interativos no dashboard (barras e rosca) |

---

## 🏗️ Arquitetura

O projeto segue uma **arquitetura em camadas por domínio**, garantindo separação clara de responsabilidades e facilitando manutenção e testes.

```
View  →  Business  →  Rules
               ↓
            Helper
```

Cada domínio (ex: `Financeiro`) contém seus próprios arquivos de camada:

```
Domínio (ex: Financeiro)/
  app (ex: lancamentos)/
    models.py    ← Herda BasicModel + mixins de composição
    views.py     ← Herda BasicView; SÓ lida com request/response
    business.py  ← Orquestra o fluxo, chama Rules/Helper, usa transaction.atomic()
    helpers.py   ← Queries reutilizáveis, funções auxiliares sem escrita no banco
    rules.py     ← Valida regras de negócio; lança exceções ou retorna False
    forms.py     ← Formulários Django ligados aos models
    urls.py      ← Rotas do domínio com namespace
    admin.py     ← Configuração do Django Admin
    tests.py     ← Suite de testes cobrindo todas as camadas
```

### Responsabilidades de cada camada

| Camada | Arquivo | O que faz |
|:---:|---|---|
| 🌐 **View** | `views.py` | Recebe a requisição, chama o Business e devolve a resposta. Zero lógica de negócio aqui. |
| ⚙️ **Business** | `business.py` | Orquestra o fluxo completo, chama Rules e Helper, e encapsula tudo em `transaction.atomic()`. |
| ✅ **Rules** | `rules.py` | Garante que as regras de negócio são respeitadas. Lança `BusinessRulesExceptions` ou retorna `False`. |
| 🔎 **Helper** | `helpers.py` | Queries complexas e reutilizáveis — somente leitura, sem efeitos colaterais. |

### Tratamento de Exceções

| Exceção | Quando é lançada | HTTP resultante |
|---|---|:---:|
| `BusinessRulesExceptions` | Regra de negócio violada (ex: valor negativo) | **400** |
| `ProcessException` | Erro tratado pelo Business (ex: categoria já existe) | **400** |
| `SystemErrorException` | Erro inesperado — capturado no `except Exception` | **500** |

---

## 📁 Estrutura de Pastas

```
hackathon/           ← ⚙️  Configurações do projeto (settings, urls, wsgi, asgi)
core/                ← 🧱  Classes base, exceções, mixins e constantes técnicas
common/              ← 📦  Constantes de texto reutilizáveis e widgets personalizados
Financeiro/          ← 💰  Domínio financeiro (app: lancamentos)
Usuario/             ← 👤  Domínio de usuário (app: autenticacao)
templates/           ← 🎨  Templates HTML organizados por domínio/app
  base.html          ─── Layout raiz (landing, login)
  base_auth.html     ─── Layout autenticado com sidebar (extends base.html)
  core/              ─── Páginas de erro personalizadas (400, 403, 404, 500)
static/              ← 🗂️  Arquivos estáticos (CSS, JS, imagens)
docs/                ← 📊  Diagramas e documentação técnica
manage.py
requirements.txt
.env-example
```

---

## 🚀 Como Executar

Siga os passos abaixo para ter o projeto rodando localmente em poucos minutos.

### 1️⃣ Clone o repositório

```bash
git clone <url-do-repositorio>
cd hackathon
```

### 2️⃣ Crie e ative o ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure as variáveis de ambiente

```bash
cp .env-example .env
# Abra o .env e preencha a SECRET_KEY e demais configurações
```

### 5️⃣ Execute as migrações

```bash
python manage.py migrate
```

### 6️⃣ Crie um superusuário *(opcional)*

```bash
python manage.py createsuperuser
```

### 7️⃣ Popule dados de demonstração *(opcional)*

```bash
python manage.py seed_demo
```

### 8️⃣ Suba o servidor

```bash
python manage.py runserver
```

> 🌐 Acesse em **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## ⚙️ Variáveis de Ambiente

Copie `.env-example` para `.env` e preencha conforme a tabela abaixo:

| Variável | Descrição | Padrão |
|---|---|:---:|
| `SECRET_KEY` | 🔑 Chave secreta do Django — **obrigatória** | — |
| `DEBUG` | 🐛 Ativa o modo debug (desative em produção) | `True` |
| `ALLOWED_HOSTS` | 🌍 Hosts permitidos, separados por vírgula | `127.0.0.1,localhost` |

> ⚠️ **Nunca** versione o arquivo `.env` nem exponha a `SECRET_KEY` publicamente.

---

## 🛣️ Rotas Principais

| Método | URL | Nome | Descrição |
|:---:|---|---|---|
| `GET` | `/` | `landing` | 🏠 Landing page pública |
| `GET/POST` | `/login/` | `usuario:login` | 🔐 Login |
| `POST` | `/logout/` | `usuario:logout` | 🚪 Logout |
| `GET` | `/financeiro/` | `financeiro:dashboard` | 📊 Dashboard financeiro |
| `GET` | `/financeiro/lancamentos/` | `financeiro:lancamento-lista` | 📋 Lista de lançamentos |
| `GET/POST` | `/financeiro/lancamentos/novo/` | `financeiro:lancamento-criar` | ➕ Criar lançamento |
| `GET/POST` | `/financeiro/lancamentos/<pk>/editar/` | `financeiro:lancamento-editar` | ✏️ Editar lançamento |
| `POST` | `/financeiro/lancamentos/<pk>/excluir/` | `financeiro:lancamento-excluir` | 🗑️ Excluir (AJAX) |
| `GET` | `/financeiro/categorias/` | `financeiro:categoria-lista` | 🏷️ Lista de categorias |
| `GET/POST` | `/financeiro/categorias/nova/` | `financeiro:categoria-criar` | ➕ Criar categoria |
| `GET/POST` | `/financeiro/categorias/<pk>/editar/` | `financeiro:categoria-editar` | ✏️ Editar categoria |
| `POST` | `/financeiro/categorias/<pk>/excluir/` | `financeiro:categoria-excluir` | 🗑️ Excluir (AJAX) |
| `GET` | `/financeiro/relatorio/` | `financeiro:relatorio` | 📄 Relatório com filtros |
| `GET` | `/financeiro/relatorio/pdf/` | `financeiro:relatorio-pdf` | ⬇️ Download PDF |
| `GET` | `/admin/` | — | 🛡️ Django Admin (superusuários) |

---

## 🧪 Testes

```bash
# Rodar toda a suite de testes
python manage.py test

# Rodar apenas os testes do módulo financeiro, com detalhes
python manage.py test Financeiro.lancamentos --verbosity=2
```

A suite de testes cobre os seguintes cenários:

| Área | O que é testado |
|---|---|
| 🔐 **Autenticação** | Redirecionamento para login em todas as rotas protegidas |
| 📊 **DashboardView** | Acesso, template correto e contexto (saldo, gráfico, últimos lançamentos) |
| 📋 **LancamentoListView** | Listagem, filtros ativos, AJAX partial e isolamento de dados entre usuários |
| ➕ **LancamentoCreateView** | GET/POST, redirecionamento após criação e isolamento |
| ✏️ **LancamentoUpdateView** | Edição completa e proteção contra acesso cruzado |
| 🗑️ **LancamentoDeleteView** | Resposta JSON de sucesso e isolamento de exclusão |
| 🏷️ **CategoriaListView / CreateView / UpdateView** | CRUD completo de categorias |
| 🗑️ **CategoriaDeleteView** | Exclusão com e sem lançamentos vinculados, isolamento |
| 📄 **RelatorioView** | Acesso, filtros e isolamento |
| 📑 **RelatorioPDFView** | Status HTTP 200 e `Content-Type: application/pdf` |

---

## 🔧 Comandos Úteis

```bash
# 🚀 Iniciar o servidor de desenvolvimento
python manage.py runserver

# 📐 Criar novas migrações após alterar models
python manage.py makemigrations

# 🗄️ Aplicar migrações ao banco
python manage.py migrate

# 👤 Criar superusuário para o admin
python manage.py createsuperuser

# 🌱 Popular banco com dados de demonstração
python manage.py seed_demo

# 🧪 Rodar todos os testes automatizados
python manage.py test

# 📦 Coletar arquivos estáticos para produção
python manage.py collectstatic

# 🩺 Verificar saúde geral do projeto
python manage.py check
```

---

## 👥 Usuários de Demonstração

Após executar `python manage.py seed_demo`, dois usuários de teste ficam disponíveis com dados pré-carregados:

| Usuário | Senha | Conteúdo |
|:---:|:---:|---|
| `demo1` | `demo1234` | 10 categorias + ~45 lançamentos variados |
| `demo2` | `demo1234` | 10 categorias + ~45 lançamentos variados |

> 🔒 Os dados de `demo1` e `demo2` são **completamente isolados** entre si — nenhum usuário enxerga os dados do outro.

---

<div align="center">

Feito com ☕ e muito Python · Hackathon Ctrl+Alt+AI · M2A / IntGest

</div>
