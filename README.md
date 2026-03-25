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
- [� Análise de IA](#-análise-de-ia)
- [🌍 Internacionalização](#-internacionalização)
- [🌙 Modo Noturno e Claro](#-modo-noturno-e-claro)
- [💱 Múltiplas Moedas](#-múltiplas-moedas)
- [�🧰 Stack e Pacotes](#-stack-e-pacotes)
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

Uma **Prova de Conceito** de software de Gestão Financeira Pessoal que traz o essencial para quem quer ter controle real sobre o próprio dinheiro — sem complicação, sem excesso, com o poder da Inteligência Artificial.

Com ele você consegue:

- 📥 **Registrar receitas e despesas** organizadas por categorias personalizadas
- 💹 **Visualizar o saldo** atualizado automaticamente em tempo real
- 📊 **Explorar um dashboard** com resumo financeiro e gráficos interativos
- ✏️ **Gerenciar lançamentos** completos: criar, editar e excluir, com dados totalmente isolados por usuário
- 📄 **Exportar relatórios filtrados** e análises de IA diretamente em PDF
- 🤖 **Receber uma análise financeira personalizada** gerada por Inteligência Artificial (OpenAI)
- 🌙 **Alternar entre modo noturno e claro** com um clique, persistindo a preferência no navegador
- 🌍 **Usar o sistema em Português ou Inglês**, com troca de idioma disponível em toda a interface
- 💱 **Visualizar os valores na sua moeda favorita**, com cotação atualizada em tempo real via AwesomeAPI

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
| 🤖 | **Análise financeira com IA** | Análise completa gerada pela OpenAI com base nos últimos 3 meses de dados |
| 📑 | **PDF da análise de IA** | Exporta o relatório de análise inteligente em PDF formatado |
| 🌙 | **Modo noturno / claro** | Alternância de tema com transição suave e preferência salva no navegador |
| 🌍 | **Português e Inglês** | Interface totalmente traduzida; troca de idioma disponível em qualquer tela |
| 💱 | **Múltiplas moedas** | Valores exibidos na moeda preferida do usuário com cotação em tempo real |
| 🔒 | **Isolamento por usuário** | Cada usuário acessa somente os próprios dados |
| 🛡️ | **Admin restrito** | Painel Django Admin disponível apenas para `is_superuser=True` |
| 🕓 | **Histórico de alterações** | `django-simple-history` registra todo o histórico de edições |

---

## 🤖 Análise de IA

O sistema integra-se à **API da OpenAI (GPT-4o-mini por padrão)** para gerar uma análise financeira personalizada com base nos lançamentos dos últimos 3 meses do usuário.

A análise contempla:

- **Fluxo de caixa** — receitas vs. despesas
- **Distribuição de gastos** por categoria
- **Evolução financeira** ao longo do tempo
- **Taxa de poupança** e relação gastos fixos × variáveis
- **Padrões de consumo** identificados automaticamente
- **Previsões** para os próximos meses
- **Alertas de risco** e sugestões práticas personalizadas

O resultado pode ser **exportado em PDF** com um único clique, com formatação profissional.

> ⚙️ Para usar a análise de IA, configure `OPENAI_API_KEY` e (opcionalmente) `OPENAI_MODEL` no arquivo `.env`.

---

## 🌍 Internacionalização

O sistema suporta **Português Brasileiro (pt-br)** e **Inglês (en)** de forma nativa, usando o sistema de i18n do Django (`i18n_patterns`, `LocaleMiddleware`, arquivos `.po`/`.mo`).

- A URL reflete o idioma ativo: `/pt-br/financeiro/` ou `/en/financeiro/`
- A troca de idioma é feita pelo seletor presente na interface, sem necessidade de recarregar manualmente
- Todos os textos do sistema estão preparados para tradução com `gettext_lazy`

---

## 🌙 Modo Noturno e Claro

O sistema possui suporte completo a **tema claro e escuro** via Bootstrap 5 (`data-bs-theme`):

- A preferência é **salva no `localStorage`** do navegador — não some ao recarregar a página
- A alternância aplica uma **transição suave** (CSS `transition`) em todos os elementos: cards, sidebar, tabelas, header e footer
- O tema padrão ao primeiro acesso é o **modo claro**
- Funciona em todas as páginas autenticadas e nas páginas públicas (landing page, login)

---

## 💱 Múltiplas Moedas

O sistema suporta exibição de valores em **qualquer moeda disponível na AwesomeAPI** (BRL, USD, EUR, GBP, JPY, BTC e muitas outras).

- Os valores são **sempre armazenados em BRL** no banco de dados
- A conversão é feita **em tempo real** na exibição, com base na cotação mais recente
- As cotações são **cacheadas localmente** (`data/cotacoes.json`) por 1 minuto para não sobrecarregar a API
- O usuário escolhe sua moeda preferida em **Configurações → Moeda**
- O símbolo da moeda é exibido em toda a interface automaticamente via context processor

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
| 📅 **python-dateutil** | 2.9.0 | Cálculos e manipulação avançada de datas |
| 🌐 **requests** | 2.32.3 | Chamadas HTTP externas (AwesomeAPI de cotações e OpenAI) |

### Inteligência Artificial

| Pacote / Serviço | Versão | Para que serve |
|---|:---:|---|
| 🤖 **OpenAI API** (via `requests`) | — | Geração da análise financeira personalizada via GPT |
| 📝 **markdown** | 3.7 | Converte a resposta da IA (Markdown) em HTML antes da exportação para PDF |

### Internacionalização

| Recurso | Para que serve |
|---|---|
| `django.middleware.locale.LocaleMiddleware` | Detecta e ativa o idioma correto a cada requisição |
| `django.conf.urls.i18n` + `i18n_patterns` | URLs prefixadas por idioma (`/pt-br/`, `/en/`) |
| `gettext_lazy` em todo o código | Prepara todos os textos para tradução |
| `locale/en/LC_MESSAGES/django.po` | Arquivo de tradução para o inglês |

### Cotação de Moedas

| Recurso | Para que serve |
|---|---|
| **AwesomeAPI** (`economia.awesomeapi.com.br`) | Fornece cotações em tempo real de +200 moedas |
| `common/currency_service.py` | Cache local de 1 min em `data/cotacoes.json`; funções de conversão |
| `common/context_processors.py` | Injeta `moeda_usuario` em todos os templates automaticamente |
| `Usuario/configuracoes` | App onde o usuário define sua moeda preferida |

### Geração de PDF

| Pacote | Versão | Para que serve |
|---|:---:|---|
| 📑 **xhtml2pdf** | 0.2.17 | Converte HTML/CSS em PDF para exportação de relatórios e análise de IA |
| `reportlab` | 4.4.10 | Motor de renderização PDF (base do xhtml2pdf) |
| `pypdf` | 6.9.2 | Manipulação de arquivos PDF já gerados |
| `html5lib` | 1.1 | Parser HTML5 utilizado pelo xhtml2pdf |

### Frontend (via CDN)

| Biblioteca | Versão | Para que serve |
|---|:---:|---|
| 🎨 **Bootstrap** | 5 | Layout responsivo, componentes, utilitários CSS e suporte a `data-bs-theme` (dark/light) |
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
common/              ← 📦  Constantes de texto, widgets, cotação de moedas e context processors
  currency_service.py   ─── Integração com AwesomeAPI + cache local de cotações
  context_processors.py ─── Injeta moeda_usuario em todos os templates
  templatetags/         ─── Tag {{ valor|moeda }} para exibição formatada
Financeiro/          ← 💰  Domínio financeiro (app: lancamentos)
  lancamentos/
    business.py      ─── Inclui gerar_analise_financeira() via OpenAI
    views.py         ─── AnaliseFinanceiraView (AJAX) + AnaliseFinanceiraPDFView
    templates/       ─── analise_pdf.html, relatorio_pdf.html, dashboard.html, …
Usuario/             ← 👤  Domínio de usuário
  autenticacao/      ─── Login, logout, landing page
  configuracoes/     ─── Preferência de moeda do usuário (app separado)
templates/           ← 🎨  Templates HTML organizados por domínio/app
  base.html          ─── Layout raiz — dark/light mode, seletor de idioma, seletor de moeda
  base_auth.html     ─── Layout autenticado com sidebar (extends base.html)
  core/              ─── Páginas de erro personalizadas (400, 403, 404, 500)
static/              ← 🗂️  Arquivos estáticos (CSS, JS, imagens)
locale/              ← 🌍  Arquivos de tradução (pt-br / en)
  en/LC_MESSAGES/    ─── django.po + django.mo (tradução para inglês)
data/                ← 💾  Cache local de cotações (cotacoes.json, TTL 1 min)
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
| `OPENAI_API_KEY` | 🤖 Chave da API OpenAI — necessária para a análise de IA | — |
| `OPENAI_MODEL` | 🧠 Modelo GPT utilizado na análise financeira | `gpt-4o-mini` |

> ⚠️ **Nunca** versione o arquivo `.env` nem exponha a `SECRET_KEY` ou `OPENAI_API_KEY` publicamente.
>
> 💡 A análise de IA é **opcional** — o restante do sistema funciona normalmente sem `OPENAI_API_KEY`.

---

## 🛣️ Rotas Principais

> As rotas são prefixadas pelo idioma ativo: `/pt-br/` (padrão) ou `/en/`.

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
| `GET` | `/financeiro/relatorio/pdf/` | `financeiro:relatorio-pdf` | ⬇️ Download PDF do relatório |
| `POST` | `/financeiro/analise/` | `financeiro:analise-financeira` | 🤖 Gerar análise financeira (AJAX → OpenAI) |
| `POST` | `/financeiro/analise/pdf/` | `financeiro:analise-pdf` | ⬇️ Download PDF da análise de IA |
| `GET/POST` | `/configuracoes/moeda/` | `configuracoes:moeda` | 💱 Configurar moeda de exibição |
| `POST` | `/i18n/set_language/` | — | 🌍 Trocar idioma (pt-br ↔ en) |
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
