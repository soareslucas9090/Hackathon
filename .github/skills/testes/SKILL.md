---
name: testes
description: |
  Skill para criar e manter testes automatizados Django (TestCase).
  USE PARA: escrever testes de views, testar AJAX, PDF, filtros, isolamento de dados
  e redirecionamento sem login. Contém padrões de setUp, assertivas e checklist de cobertura.
---

# SKILL — Testes Automatizados

## Quando usar esta skill

Use quando for necessário:
- Criar testes para novas views ou módulos
- Corrigir ou expandir testes existentes
- Entender como testar AJAX, PDF, filtros e isolamento de dados

## Padrão base de TestCase

```python
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date
import json

User = get_user_model()

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.client2 = Client()

        self.usuario = User.objects.create_user("testuser", "test@test.com", "senha123")
        self.outro_usuario = User.objects.create_user("outro", "outro@test.com", "senha123")

        self.client.force_login(self.usuario)
        self.client2.force_login(self.outro_usuario)
```

## O que testar em cada tipo de View

### BasicTableView (listagem)
```python
def test_listagem_retorna_200(self):
    response = self.client.get(reverse("namespace:lista"))
    self.assertEqual(response.status_code, 200)

def test_lista_apenas_proprios_dados(self):
    response = self.client.get(reverse("namespace:lista"))
    qs = response.context["object_list"]
    for obj in qs:
        self.assertEqual(obj.usuario, self.usuario)

def test_ajax_retorna_partial(self):
    response = self.client.get(
        reverse("namespace:lista"),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "app/partials/tabela.html")
```

### BasicCreateView
```python
def test_get_retorna_200(self):
    response = self.client.get(reverse("namespace:criar"))
    self.assertEqual(response.status_code, 200)

def test_post_valido_cria_objeto(self):
    total_antes = MeuModel.objects.filter(usuario=self.usuario).count()
    self.client.post(reverse("namespace:criar"), {...dados_validos...})
    self.assertEqual(MeuModel.objects.filter(usuario=self.usuario).count(), total_antes + 1)

def test_post_valido_redireciona(self):
    response = self.client.post(reverse("namespace:criar"), {...dados_validos...})
    self.assertRedirects(response, reverse("namespace:lista"))
```

### BasicUpdateView
```python
def test_nao_edita_dado_de_outro_usuario(self):
    response = self.client.get(
        reverse("namespace:editar", args=[self.objeto_de_outro.pk])
    )
    self.assertEqual(response.status_code, 404)
```

### BasicActionView (AJAX / exclusão)
```python
def test_delete_proprio_objeto(self):
    response = self.client.post(
        reverse("namespace:excluir", args=[self.objeto.pk]),
        content_type="application/json",
    )
    data = json.loads(response.content)
    self.assertTrue(data["success"])
    self.assertFalse(MeuModel.objects.filter(pk=self.objeto.pk).exists())

def test_delete_objeto_alheio_retorna_erro(self):
    response = self.client.post(
        reverse("namespace:excluir", args=[self.objeto_de_outro.pk]),
        content_type="application/json",
    )
    data = json.loads(response.content)
    self.assertFalse(data["success"])
```

### PDF View
```python
def test_retorna_pdf(self):
    response = self.client.get(reverse("namespace:relatorio-pdf"))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "application/pdf")
```

### Proteção de autenticação
```python
class RedirecionamentoSemLoginTest(TestCase):
    def test_rota_protegida_redireciona(self):
        response = self.client.get(reverse("namespace:lista"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])
```

## Regras de teste

- Use `force_login()` — nunca `login()` com senha, pois é mais lento.
- Cada `setUp` deve ser independente — não dependa de ordem de execução.
- Teste o **isolamento de dados** em toda view que retorna dados do usuário.
- Para `BasicActionView`, sempre verifique `data["success"]` no JSON retornado.
- Não teste internals do Business/Rules diretamente — teste **comportamento da View**.
- Use `assertRedirects` para verificar redirecionamentos pós-formulário.

## Executar apenas um módulo

```bash
python manage.py test Financeiro.lancamentos --verbosity=2
```

## Executar todos os testes

```bash
python manage.py test
```

## Cobertura de testes esperada por módulo

Todo módulo novo deve cobrir:
- [ ] Redirecionamento sem login
- [ ] GET da listagem (200)
- [ ] Isolamento: usuário não vê dados de outro
- [ ] AJAX partial na listagem
- [ ] GET do formulário de criação (200)
- [ ] POST válido cria objeto
- [ ] POST válido redireciona
- [ ] Objeto criado pertence ao usuário logado
- [ ] GET do formulário de edição (200)
- [ ] POST atualiza o objeto
- [ ] Edição de objeto alheio retorna 404
- [ ] Exclusão do próprio objeto (JSON success)
- [ ] Exclusão de objeto alheio (JSON error)
