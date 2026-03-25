# Diagramas do Sistema — Gestão Financeira Pessoal

Diagramas Mermaid e PlantUML descrevendo a arquitetura, modelos e fluxos do sistema.

---

## 1. Arquitetura em Camadas

### Mermaid

```mermaid
graph TD
    subgraph Request
        HTTP[HTTP Request]
    end

    subgraph View["View (views.py)"]
        V[BasicView\nRecebe request\nChama Business\nRetorna response]
    end

    subgraph Business["Business (business.py)"]
        B[ModelBusiness\nOrquestra o fluxo\ntransaction.atomic]
    end

    subgraph Rules["Rules (rules.py)"]
        R[ModelRules\nValida regras\nLanca excecoes]
    end

    subgraph Helper["Helper (helpers.py)"]
        H[ModelHelper\nQueries reutilizaveis\nFuncoes auxiliares]
    end

    subgraph ModelLayer["Model (models.py)"]
        M[BasicModel\nORM Django\nHistory]
    end

    subgraph Excecoes["Excecoes"]
        E1[BusinessRulesExceptions - HTTP 400]
        E2[ProcessException - HTTP 400]
        E3[SystemErrorException - HTTP 500]
    end

    HTTP --> V
    V --> B
    B --> R
    B --> H
    B --> M
    R -- lanca --> E1
    B -- lanca --> E2
    B -- lanca --> E3
```

### PlantUML

```plantuml
@startuml Arquitetura em Camadas
skinparam packageStyle rectangle
left to right direction

package "HTTP" {
  [Request]
}

package "View (views.py)" {
  [BasicView] as V
  note right of V : Recebe request\nChama Business\nRetorna response
}

package "Business (business.py)" {
  [ModelBusiness] as B
  note right of B : Orquestra o fluxo\ntransaction.atomic()
}

package "Rules (rules.py)" {
  [ModelRules] as R
  note right of R : Valida regras\nLanca excecoes
}

package "Helper (helpers.py)" {
  [ModelHelper] as H
  note right of H : Queries reutilizaveis\nFuncoes auxiliares
}

package "Model (models.py)" {
  [BasicModel] as M
  note right of M : ORM Django\nHistorico (simple-history)
}

package "Excecoes" {
  [BusinessRulesExceptions] as E1
  [ProcessException] as E2
  [SystemErrorException] as E3
}

[Request] --> V
V --> B
B --> R
B --> H
B --> M
R ..> E1 : lanca (400)
B ..> E2 : lanca (400)
B ..> E3 : lanca (500)
@enduml
```

---

## 2. Diagrama de Classes — Models

### Mermaid

```mermaid
classDiagram
    class BasicModel {
        +DateTimeField created_at
        +DateTimeField updated_at
        +HistoricalRecords history
    }

    class BusinessModelMixin {
        +business_class
        -_business
        +business property
        -_get_business_class()
    }

    class HelperModelMixin {
        +helper_class
        -_helper
        +helper property
    }

    class RulesModelMixin {
        +rules_class
        -_rules
        +rules property
    }

    class Categoria {
        +CharField nome
        +CharField descricao
        +CharField cor
        +FK usuario
    }

    class Lancamento {
        +CharField tipo
        +CharField descricao
        +DecimalField valor
        +DateField data
        +TextField observacao
        +FK categoria
        +FK usuario
        +TIPO_RECEITA receita
        +TIPO_DESPESA despesa
    }

    class User {
        +CharField username
        +CharField password
        +BooleanField is_superuser
    }

    BasicModel <|-- Categoria
    BasicModel <|-- Lancamento
    BusinessModelMixin <|-- Categoria
    HelperModelMixin <|-- Categoria
    RulesModelMixin <|-- Categoria
    BusinessModelMixin <|-- Lancamento
    HelperModelMixin <|-- Lancamento
    RulesModelMixin <|-- Lancamento
    Categoria "1" --> "0..*" Lancamento : lancamentos
    User "1" --> "0..*" Categoria : categorias
    User "1" --> "0..*" Lancamento : lancamentos
```

### PlantUML

```plantuml
@startuml Diagrama de Classes - Models
skinparam classAttributeIconSize 0

abstract class BasicModel {
  + created_at : DateTimeField
  + updated_at : DateTimeField
  + history : HistoricalRecords
}

class BusinessModelMixin {
  + business_class
  - _business
  + business : property
  - _get_business_class()
}

class HelperModelMixin {
  + helper_class
  - _helper
  + helper : property
}

class RulesModelMixin {
  + rules_class
  - _rules
  + rules : property
}

class Categoria {
  + nome : CharField[100]
  + descricao : CharField[255]
  + cor : CharField[7]
  + usuario : ForeignKey
}

class Lancamento {
  + tipo : CharField[receita|despesa]
  + descricao : CharField[255]
  + valor : DecimalField[12,2]
  + data : DateField
  + observacao : TextField
  + categoria : ForeignKey(PROTECT)
  + usuario : ForeignKey
}

class User {
  + username : CharField
  + password : CharField
  + is_superuser : BooleanField
}

BasicModel <|-- Categoria
BasicModel <|-- Lancamento
BusinessModelMixin <|-- Categoria
HelperModelMixin <|-- Categoria
RulesModelMixin <|-- Categoria
BusinessModelMixin <|-- Lancamento
HelperModelMixin <|-- Lancamento
RulesModelMixin <|-- Lancamento

Categoria "1" o-- "0..*" Lancamento : lancamentos >
User "1" o-- "0..*" Categoria : categorias >
User "1" o-- "0..*" Lancamento : lancamentos >
@enduml
```

---

## 3. Diagrama de Sequência — Criar Lançamento

### Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant View as LancamentoCreateView
    participant Form as LancamentoForm
    participant Business as LancamentoBusiness
    participant Rules as LancamentoRules
    participant DB as SQLite

    Usuario->>View: POST /financeiro/lancamentos/novo/
    View->>Form: form.is_valid()
    alt Formulario invalido
        Form-->>View: errors
        View-->>Usuario: 200 form com erros
    else Formulario valido
        View->>View: obj.usuario = request.user
        View->>Business: obj.business.criar()
        Business->>Rules: validar_valor()
        alt Valor invalido
            Rules-->>Business: BusinessRulesExceptions
            Business-->>View: re-raise
            View-->>Usuario: 400 Bad Request
        else Valor valido
            Rules-->>Business: OK
        end
        Business->>Rules: validar_categoria_do_usuario()
        alt Categoria de outro usuario
            Rules-->>Business: BusinessRulesExceptions
            Business-->>View: re-raise
            View-->>Usuario: 400 Bad Request
        else Categoria valida
            Rules-->>Business: OK
        end
        Business->>DB: save dentro de transaction.atomic
        DB-->>Business: OK
        Business-->>View: Sucesso
        View-->>Usuario: 302 Redirect para lista
    end
```

### PlantUML

```plantuml
@startuml Sequência - Criar Lançamento
actor Usuario
participant "LancamentoCreateView" as View
participant "LancamentoForm" as Form
participant "LancamentoBusiness" as Business
participant "LancamentoRules" as Rules
database "SQLite" as DB

Usuario -> View : POST /financeiro/lancamentos/novo/
View -> Form : is_valid()

alt Formulário inválido
    Form --> View : errors
    View --> Usuario : 200 form com erros
else Formulário válido
    View -> View : obj.usuario = request.user
    View -> Business : obj.business.criar()
    Business -> Rules : validar_valor()
    alt Valor inválido (≤ 0)
        Rules --> Business : raise BusinessRulesExceptions
        Business --> View : re-raise
        View --> Usuario : 400 Bad Request
    else Valor válido
        Rules --> Business : OK
    end
    Business -> Rules : validar_categoria_do_usuario()
    alt Categoria de outro usuário
        Rules --> Business : raise BusinessRulesExceptions
        Business --> View : re-raise
        View --> Usuario : 400 Bad Request
    else Categoria válida
        Rules --> Business : OK
    end
    Business -> DB : save() [transaction.atomic]
    DB --> Business : OK
    Business --> View : Sucesso
    View --> Usuario : 302 → lista de lançamentos
end
@enduml
```

---

## 4. Fluxo de Autenticação

### Mermaid

```mermaid
flowchart TD
    A([Usuario acessa rota protegida]) --> B{Autenticado?}
    B -- Nao --> C[Redireciona para login]
    C --> D[Preenche usuario e senha]
    D --> E{Credenciais validas?}
    E -- Nao --> F[Exibe erro no formulario]
    F --> D
    E -- Sim --> G[Redireciona para dashboard]
    B -- Sim --> H[Exibe a pagina]
    H --> I{Dados pertencem ao usuario?}
    I -- Nao --> J[404 Not Found]
    I -- Sim --> K([Renderiza conteudo])
```

### PlantUML

```plantuml
@startuml Fluxo de Autenticação
start
:Usuário acessa rota protegida;
if (Autenticado?) then (sim)
  :Carrega conteúdo da view;
  if (Dado pertence ao usuário?) then (sim)
    :Renderiza resposta;
  else (não)
    :404 Not Found;
    stop
  endif
else (não)
  :Redireciona para /login/;
  repeat
    :Preenche credenciais;
    if (Credenciais válidas?) then (sim)
      break
    else (não)
      :Exibe erro no formulário;
    endif
  repeat while (Tentar novamente?)
  :Redireciona para dashboard;
endif
stop
@enduml
```

---

## 5. Estrutura de Rotas

### Mermaid

```mermaid
graph LR
    ROOT["/"] --> LANDING[LandingPageView]
    LOGIN["/login/"] --> LOGIN_VIEW[CustomLoginView]
    LOGOUT["/logout/"] --> LOGOUT_VIEW[CustomLogoutView]

    FIN["/financeiro/"] --> DASH[DashboardView]
    FIN --> LANC["/lancamentos/"]
    FIN --> CAT["/categorias/"]
    FIN --> REL["/relatorio/"]
    FIN --> PDF["/relatorio/pdf/"]

    LANC --> LANC_LIST[LancamentoListView]
    LANC --> LANC_NEW["/novo/ - CreateView"]
    LANC --> LANC_EDIT["/pk/editar/ - UpdateView"]
    LANC --> LANC_DEL["/pk/excluir/ - DeleteView AJAX"]

    CAT --> CAT_LIST[CategoriaListView]
    CAT --> CAT_NEW["/nova/ - CreateView"]
    CAT --> CAT_EDIT["/pk/editar/ - UpdateView"]
    CAT --> CAT_DEL["/pk/excluir/ - DeleteView AJAX"]

    REL --> REL_VIEW[RelatorioView]
    PDF --> PDF_VIEW[RelatorioPDFView]

    ADMIN["/admin/"] --> ADMIN_VIEW[Django Admin\nsuperuser only]
```

### PlantUML

```plantuml
@startuml Estrutura de Rotas
left to right direction
skinparam packageStyle rectangle

package "Público" {
  [GET /] as landing
  [GET /login/] as login
  [POST /logout/] as logout
}

package "financeiro: (LoginRequired)" {
  [GET /financeiro/] as dashboard
  [GET /financeiro/lancamentos/] as lanc_lista
  [GET/POST /financeiro/lancamentos/novo/] as lanc_new
  [GET/POST /lancamentos/<pk>/editar/] as lanc_edit
  [POST /lancamentos/<pk>/excluir/] as lanc_del
  [GET /financeiro/categorias/] as cat_lista
  [GET/POST /financeiro/categorias/nova/] as cat_new
  [GET/POST /categorias/<pk>/editar/] as cat_edit
  [POST /categorias/<pk>/excluir/] as cat_del
  [GET /financeiro/relatorio/] as relatorio
  [GET /financeiro/relatorio/pdf/] as relatorio_pdf
}

package "Admin (superuser only)" {
  [GET /admin/] as admin
}

cloud "Browser" as B
B --> landing
B --> login
B --> dashboard
B --> lanc_lista
B --> relatorio
B --> admin
@enduml
```

---

## 6. Diagrama de Estados — Lançamento

### Mermaid

```mermaid
stateDiagram-v2
    [*] --> Inexistente
    Inexistente --> Ativo : criar - valor valido e categoria valida
    Ativo --> Ativo : atualizar
    Ativo --> Inexistente : excluir
    Ativo --> Historico : qualquer alteracao registrada pelo simple-history
    Historico --> [*] : consulta historico
```

### PlantUML

```plantuml
@startuml Estados - Lançamento
[*] --> Inexistente
Inexistente --> Ativo : criar()\n[valor > 0, categoria do usuário]
Ativo --> Ativo : atualizar()
Ativo --> Inexistente : excluir()
Ativo --> Historico : qualquer alteração\n(django-simple-history)
Historico --> [*] : consulta histórico
@enduml
```
