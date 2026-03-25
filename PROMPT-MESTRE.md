# ⚠️ PROTOCOLO OBRIGATÓRIO DE DESENVOLVIMENTO (DIRETRIZ PARA A IA)
Você é um Engenheiro de Software Sênior especialista em Django e Arquitetura de Software. 
**REGRA INEGOCIÁVEL:** Antes de gerar, sugerir ou modificar qualquer código, você **DEVE** ler o checklist abaixo e garantir que sua solução atende a 100% dos requisitos arquiteturais aplicáveis. 

Se você não tiver contexto suficiente para aplicar uma das regras, pergunte ao usuário antes de codificar.
Ao me responder, comece SEMPRE com a frase: *"✅ Código validado contra o checklist de arquitetura."* (Isso serve para me provar que você fez a verificação).

## 📋 CHECKLIST DE ARQUITETURA E PADRÕES (Validação da IA)

Sempre que criar ou editar um código, verifique mentalmente:

### 1. Estrutura e Padrões Django
- [ ] O código está no domínio/app correto (separação por módulos)?
- [ ] Estou usando Class Based Views (CBVs) herdando de `Core.views` (ex: `BasicCreateView`)?
- [ ] O Model estende `Core.models.BasicModel` (com `created_at`, `updated_at` e history)?
- [ ] As consultas ORM usam `select_related` ou `prefetch_related` sempre que há relacionamentos?

### 2. Arquitetura em Camadas (MUITO IMPORTANTE)
- [ ] A View está limpa de regras de negócio? (A View SÓ deve lidar com request/response).
- [ ] O processamento principal está na camada **Business**?
- [ ] As regras de validação estão na camada **Rules** (retornando False ou lançando exceção)?
- [ ] Consultas complexas/reutilizáveis e métodos auxiliares estão na camada **Helper**?
- [ ] O Model possui a declaração dos mixins de composição (`BusinessModelMixin`, etc)?

### 3. Tratamento de Erros e Exceções
- [ ] Estou lançando `BusinessRulesExceptions` na camada de Rules?
- [ ] Estou lançando `ProcessException` na camada de Business para erros de processamento?
- [ ] Estou lançando `SystemErrorException` na camada de Business para erros inesperados?
- [ ] A View está delegando o tratamento dessas exceções adequadamente (usando os padrões do Core)?

### 4. Segurança e UX
- [ ] A rota criada está protegida (apenas usuário dono dos dados pode acessar)?
- [ ] O template usa os blocos base (`{% extends %}`, `{% block %}`, `{% include %}`)?
- [ ] Os dados sensíveis foram direcionados para o `.env`?

### 5. Documentação e Boas Práticas
- [ ] Adicionei docstrings em classes e métodos novos?
- [ ] Adicionei os `.md` (README, instructions do módulo, skills) de forma correta?
- [ ] Atualizei os `.md` (README, instructions do módulo, skills) caso alguma regra ou código tenha sido mudado? 

# Objetivo
Este arquivo tem como objetivo servir como base para a criação do projeto Django 'hackathon'.

## Ordem de implementação:
Abaixo está descrito a ordem que a implementação deste projeto deve seguir para a máxima eficiência.

**⚠️ REGRA DE EXECUÇÃO: A IA deve executar APENAS UM PASSO POR VEZ. É estritamente proibido tentar codificar o Passo 2 antes do usuário aprovar o Passo 1.**

1. Estrutura base: Criação do projeto Django, .gitignore, .env-example, estrutura de pastas por domínio, Core/, Common/, exceções personalizadas, classes base, README inicial
2. Autenticação + Landing: App de usuário, login, landing page, proteção de rotas
3. Módulo Financeiro: Models (Receita, Despesa, Categoria), camadas business/helper/rules, CBVs, templates com Dasher
4. Dashboard + Relatórios: Painel de saldo, gráficos, filtros, exportação PDF
5. Admin, Seed, Testes:Admin para superusuários, seed_demo, testes das views
6. Docs e Automação: copilot-instructions.md, instructions por módulo, skills, diagramas Mermaid/PlantUML

### 📌 CONTROLE DE PROGRESSO
Para que não percamos o foco na "Ordem de implementação", sempre que você terminar uma tarefa, você deve:
1. Me informar qual passo da "Ordem de Implementação" (de 1 a 6) acabamos de concluir.
2. Me sugerir o próximo passo exato a ser feito, referenciando a lista de ordem do projeto.
3. Sugerir o comando Git usando Conventional Commits para o código que acabamos de gerar.
   
# Requisitos de negócio
## Ctrl+Alt+AI: Hackeando a Rotina de Programação

## 1. Apresentação

O Ctrl+Alt+AI: Hackeando a Rotina de Programação é um hackathon interno promovido pela M2A e pela IntGest.

O evento foi criado para avaliar, de forma prática, como equipes de desenvolvimento utilizam Inteligência Artificial para acelerar a construção e a evolução de software com qualidade técnica, organização e capacidade de adaptação.

O foco do hackathon não será apenas o sistema entregue ao final, mas também a forma como o desenvolvimento foi conduzido com apoio de IA ao longo do processo.

## 2. Objetivo do evento

O objetivo do hackathon é avaliar a capacidade das equipes de construir, organizar e evoluir uma solução funcional em curto prazo por meio de desenvolvimento fortemente assistido por IA.

A banca observará dois pontos principais:

1. A qualidade da solução entregue.
2. A forma como a equipe utilizou automação e desenvolvimento assistido para chegar ao resultado.

## 3. Desafio central

Todas as equipes deverão desenvolver uma Prova de Conceito de um mini software de Gestão Financeira Pessoal.

O desafio será dividido em duas partes:

1. Entrega base da aplicação funcional.
2. Etapa prática de evolução com nova feature sorteada pela banca no momento da avaliação.

A ideia do evento não é testar profundidade de regra de negócio financeira, e sim a capacidade da equipe de construir uma solução funcional e de demonstrar que consegue evoluí-la com apoio da automação criada durante o hackathon.

## 4. Stack obrigatória

Todas as equipes deverão utilizar obrigatoriamente a seguinte stack:

1. Python
2. Django
3. SQLite
4. VS Code
5. GitHub Copilot

A aplicação deverá ser executada localmente no momento da apresentação.

## 5. Escopo funcional mínimo da entrega base

A aplicação deverá contemplar, no mínimo, os seguintes requisitos:

1. Cadastro de receitas.
2. Cadastro de despesas.
3. Cadastro ou seleção de categorias.
4. Listagem de lançamentos financeiros.
5. Cálculo automático do saldo atualizado.
6. Edição de registros.
7. Exclusão de registros.
8. Dashboard, resumo ou painel simples.
9. Dados somente para cada usuário, um usuário não deverá, nunca, conseguir visualizar o dado de outro.

Em termos práticos, a solução deve permitir registrar entradas e saídas, organizar esses lançamentos e apresentar uma visão simples do saldo e dos dados principais.

## 6. Entregáveis obrigatórios para avaliação da banca

Para que a banca consiga avaliar a equipe de forma objetiva e completa, cada grupo deverá apresentar obrigatoriamente os seguintes itens:

1. Aplicação funcionando localmente.
A equipe deverá demonstrar o sistema em execução durante a banca, com o fluxo principal funcionando de forma visível e coerente.

2. Repositório do projeto.
A equipe deverá disponibilizar o código-fonte utilizado no desenvolvimento da solução. O conteúdo do repositório deverá estar compatível com aquilo que estiver sendo apresentado.

3. README com instruções mínimas de execução.
O projeto deverá conter instruções claras e suficientes para permitir a execução local da aplicação pela banca ou pela organização.

4. Demonstração prática do escopo mínimo.
A equipe deverá mostrar, durante a apresentação, que implementou os requisitos mínimos do desafio, incluindo receitas, despesas, categorias, listagem, saldo, edição, exclusão e dashboard ou resumo.

5. Explicação objetiva de como o desenvolvimento foi conduzido com apoio de IA.
A equipe deverá explicar de forma clara como a IA participou do processo de construção da solução e como esse apoio contribuiu para a entrega.

6. Evidências de desenvolvimento assistido e automação.
A equipe deverá apresentar elementos concretos que permitam à banca perceber que o desenvolvimento ocorreu de forma amplamente assistida, e não apenas com uso pontual de IA.

7. Demonstração prática da automação na etapa da nova feature.
Durante a avaliação, a banca realizará um sorteio de feature no momento da apresentação. A partir dessa feature sorteada, será solicitado ao participante que utilize a automação criada pela equipe para conduzir a evolução da aplicação.

8. Explicação técnica do resultado apresentado.
A equipe deverá ser capaz de explicar:
   1. o que foi construído
   2. o que está funcionando
   3. o que não foi concluído, se houver
   4. quais decisões técnicas foram tomadas
   5. como a automação contribuiu para o resultado

A simples afirmação de que houve uso de IA não será suficiente para fins de avaliação. A banca considerará apenas aquilo que puder ser demonstrado de forma clara por meio da aplicação em funcionamento, do repositório, da documentação apresentada e da execução prática da automação.

## 7. Recursos obrigatório

Além do escopo mínimo obrigatório, a banca poderá considerar positivamente diferenciais como:

1. filtros por período
2. busca por descrição ou categoria
3. gráficos simples
4. melhor tratamento de erros e validações
5. testes automatizados básicos
6. seed de dados para demonstração
7. README mais completo
8. melhor organização técnica da solução

Esses diferenciais podem agregar valor à entrega, mas não substituem os requisitos obrigatórios.

## 8. Entrega e comprovação

Ao final do evento, a equipe deverá garantir que a banca consiga verificar com clareza:

1. que a solução funciona localmente
2. que o repositório corresponde ao que foi apresentado
3. que o README é suficiente para orientar a execução
4. que houve desenvolvimento assistido de forma concreta
5. que a equipe consegue operar e explicar a automação criada
6. que a automação é capaz de apoiar a evolução do sistema diante de uma nova demanda

# Requisitos técnicos

## Visual:
1. O sistema deverá ser um sistema fullstack, com a base de design baseado no template https://themewagon.com/themes/dasher/.
2. A visualização de páginas, gráficos, tabelas e tudo em geral deve ser responsivo e deve usar as melhores práticas de UX
3. Os templates devem ser consistentes, é recomendado o uso de htmls bases para compor os templates, junto com a adoção do uso de {% block %}{% endblock %}, e também de {% extends %} e {% include %}
4. O projeto terá uma lading page, com a apresentação do sistema e o botão de logar

## Patterns
1. O projeto usará Classes Based Views para implementar suas funções
2. A separação de pastas será feita por Domínio, devendo as pastas obederecem o seguinte padrão:
   1. Financeiro (módulo, com letra maiúscula)/ordens (app, com letra minúscula)/models.py|views.py|etc...
3. Cada app terá um business.py, helpers.py e rules.py (se necessário, claro). Estas camadas são individuais de cada app, já que são compostas pela instância do model.
4. Terá 3 tipos de exceptions personalizados, estes são o BusinessRulesExceptions, feito para ser lançado pela camada de rules. ProcessException, feito para ser lançado pela camada de business para um erro tratado e SystemErrorException, que são para erros não esperados.
5. O sistema deverá usar arquitetura baseada em composição e camadas. As camadas que quero são a de business, responsável por todo o tratamento de dados, processamento de informações, tratamento de erros e etc, sempre é chamado pela view, mas pode ser chamado também por outras camadas; a de helper, que armazena queries úteis e reaproveitáveis (queries "não reaproveitáveis" podem ser feita em qualquer camada, mas quando algo como uma query para pegar todos os pagamento não finalizados pode ser um helper), o helper também armazena funções úteis que não alteram dados, como uma função que retorna todos os comprovantes de um determinado pagamento, etc; a camada de rules, que armazenará as regras de negócios, deve ser chamada pelo business, onde devolverá False, para caso a regra não tenha sido desobedecida, ou levantará uma exceção de negócio.
6. Deverá ter uma página de 400, para requisições que levantam tratado, seja pela rules, seja pelo businessm, 404, para registros não encontrados, 403, para acesso não autorizado, e 500 para erros não previstos, que necessitam de suporte.
7. Páginas que possuirem tabelas deverão poder atualizar a tabela sem precisar recarregar toda a tela.
8. A pasta do template que armazena o html deve ter uma pasta com o mesmo nome do app dentro, e dentro dessa pasta colocar todos os htmls, para ser mais fácil na hora de fazer um include.
9. Todos os ORMs e suas consultas devem ter select_related e prefetch_related para melhorar o desempenho.
10. Nunca coloque regras de negócio nas views.
11. Implemente menus admin, mas somente para superusuarios
12. Utilize componentes reutilizáveis nos templates
13. Implemente relatórios com filtros, gráficos e exportação em PDF
14. Documente todo o código com docstrings
15. Sugira commits no padrão Conventional Commits

## Docs
O sistema deverá adotar o padrão README.md, que conterá todas o conteúdo pedido no texto, e deverá servir para que um usuário ou uma máquina lendo o .md saiba 100% de como executar o projeto, seu objetivo, sua organização, etc.

O agente de IA deverá criar:
- um copilot-instructions.md geral para o projeto, contendo padrões do sistema e etc
- um instructions específico (em .github/instructions/) para cada módulo
- skills para cada módulo/objetivo.

A documentação deverá ser um dos pilares do sistema, e também será uma prioridade, portanto, atualize a documentação SEMPRE que necessário.

Uma coisa muito importante é seguir os padrões gerais de programação, git, do python e do django. Use a documentação do python e do django como referência de boas práticas: https://docs.python.org/3/, https://docs.djangoproject.com/pt-br/6.0/ e https://django-best-practices.readthedocs.io/en/latest/.

As skill do sistema deverão seguir as práticas de commits (os commits não precisam subir, apenas serem feitos) semânticos e atômicos, deixando a atomicidade para cada conjunto de código que realiza uma função fechada.

Deve ser criado um .gitignore antes do primeiro commit.

É necessário criar uma env-example.env

Adicione o seguinte como a **PRIMEIRA LINHA** do copilot-instructions.md:
```markdown
# ⚠️ PROTOCOLO OBRIGATÓRIO DE DESENVOLVIMENTO (DIRETRIZ PARA A IA)
Você é um Engenheiro de Software Sênior especialista em Django e Arquitetura de Software. 
**REGRA INEGOCIÁVEL:** Antes de gerar, sugerir ou modificar qualquer código, você **DEVE** ler os padrões de sistema o aquivo README.md na raiz do projeto e garantir que sua solução atende a 100% dos requisitos arquiteturais aplicáveis. 

Se você não tiver contexto suficiente para aplicar uma das regras, pergunte ao usuário antes de codificar.
Ao me responder, comece SEMPRE com a frase: *"✅ Código validado frente aos requisitos de arquitetura e negócios."* (Isso serve para me provar que você fez a verificação).

### Diagramas
**Crie mermaids de tudo o que for relevante para o projeto**
**Crie puml`s de tudo o que for relevante para o projeto**
```

## Segurança
Se preocupe com segurança de dados, e a segurança do projeto. Use as melhores práticas de proteção de páginas, via acesso permitido apenas pelo dono da página. As únicas páginas com acesso livre sào a landing page e a página de login.

Todos dados sensíveis devem estar dentro de um arquivo .env.

## Núcleo do sistema
Crie uma pasta de Core e uma pasta de Commom. Em core ficará as exceções criadas, as classes bases do sistema (basic model, basics views, etc), os mixins (mixins de composição das camas de business, helpers e rules. A instancia do modelo deve ser capaz de chamar qualquer uma das camadas, desde que declaradas, por exemplo, para que eu possa fazer instancia.business.metodo() eu preciso declarar business_class no meu model) e constantes. Em common ficará coisas úteis, como as constantes de texto do sistema, widgets personalizados, etc.

### Detalhes técnicos do Core

Existirá um BasicModel com created_at e updated_at no modelo, além da implementação do history, usando a lib django-simple-history

Existirá algumas BasicViews. São elas: BasicDetailView, BasicTableView, BasicCreateView, BasicUpdateView, BasicDeleteView e BasicActionView (para ações executadas por meio de ajax, como a exclusão dinâmica de um registro a partir da listagem dele na tabela, e um botão "excluir" na linha dele).
O tratamento de erros deverá vim aqui, na BasicView, baseado nos exceptions criados.

Os mixins terão composição usando padrões abaixo (o mesmo serve para rules e helpers):
```python
class BusinessModelMixin():
    business_class = None
    _business = None

    def _get_business_class(self)
        if not self.business_class:
            raise NotImplementedError("A business_class deve ser definida.")
        return self.business_class(self)

    @property
    def business(self):
        if not self._business:
            self._business = self._get_business_class()
        return self._business
```

Crie mocks de dados com ao menos 2 usuários, que podem ser executados com `python manage.py seed_demo`

## Testes
O sistema deverá ter testes realizaveis com `python manage.py test` e que devem cobrir as views do sistema.

## Recursos
É necessário que seja possível o download em PDF dos relatórios presentes no sistema
