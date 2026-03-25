# Gestão Financeira Pessoal

Sistema web para controle de finanças pessoais, desenvolvido em Django com arquitetura em camadas como parte do Hackathon **Ctrl+Alt+AI: Hackeando a Rotina de Programação**.

---

## Sumário

- [Objetivo](#objetivo)
- [Stack](#stack)
- [Arquitetura](#arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Como Executar](#como-executar)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Comandos Úteis](#comandos-úteis)

---

## Objetivo

Prova de Conceito de um mini software de **Gestão Financeira Pessoal** que permite:

- Registrar receitas e despesas com categorias.
- Visualizar saldo atualizado automaticamente.
- Ver um dashboard com resumo financeiro.
- Gerenciar lançamentos (criar, editar, excluir) com dados isolados por usuário.

---

## Stack

| Tecnologia | Versão |
|---|---|
| Python | 3.x |
| Django | 6.0.3 |
| SQLite | — |
| django-simple-history | 3.11.0 |
| python-decouple | 3.8 |

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
Financeiro/          ← Domínio financeiro (apps: lancamentos, categorias…)
Usuario/             ← Domínio de usuário (app: autenticacao)
templates/           ← Templates HTML organizados por app
  base.html
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
# Rodar testes
python manage.py test

# Gerar dados de demonstração
python manage.py seed_demo

# Coletar arquivos estáticos
python manage.py collectstatic
```

---

## Testes

```bash
python manage.py test
```

Os testes cobrem as Views principais do sistema.
