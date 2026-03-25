"""
Testes automatizados do módulo Financeiro.

Cobertura:
- DashboardView
- LancamentoListView (listagem + AJAX)
- LancamentoCreateView
- LancamentoUpdateView
- LancamentoDeleteView (AJAX)
- CategoriaListView
- CategoriaCreateView
- CategoriaUpdateView
- CategoriaDeleteView (AJAX)
- RelatorioView
- RelatorioPDFView
- AnaliseFinanceiraView (AJAX + mock OpenAI)
- Isolamento entre usuários (usuário A não vê dados de B)

Execução::

    python manage.py test Financeiro.lancamentos.tests
"""
import json
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Categoria, Lancamento

User = get_user_model()


# ─────────────────────────────────────────── Mixins de apoio ─────────────────

class BaseFinanceiroTestCase(TestCase):
    """
    Caso de teste base com dois usuários, categorias e lançamentos pré-criados.

    Cada subclasse herda:
    - self.usuario, self.client (logado como usuario)
    - self.outro_usuario, self.client2 (logado como outro_usuario)
    - self.categoria, self.outro_categoria
    - self.lancamento, self.outro_lancamento
    """

    def setUp(self):
        self.client = Client()
        self.client2 = Client()

        self.usuario = User.objects.create_user(
            username="testuser", password="senha123", email="test@test.com"
        )
        self.outro_usuario = User.objects.create_user(
            username="outro", password="senha123", email="outro@test.com"
        )

        self.client.force_login(self.usuario)
        self.client2.force_login(self.outro_usuario)

        self.categoria = Categoria.objects.create(
            nome="Alimentação", cor="#f97316", usuario=self.usuario
        )
        self.outro_categoria = Categoria.objects.create(
            nome="Moradia", cor="#6366f1", usuario=self.outro_usuario
        )

        self.lancamento = Lancamento.objects.create(
            descricao="Salário",
            tipo=Lancamento.TIPO_RECEITA,
            valor=Decimal("3000.00"),
            data=date.today(),
            categoria=self.categoria,
            usuario=self.usuario,
        )
        self.outro_lancamento = Lancamento.objects.create(
            descricao="Aluguel",
            tipo=Lancamento.TIPO_DESPESA,
            valor=Decimal("1200.00"),
            data=date.today(),
            categoria=self.outro_categoria,
            usuario=self.outro_usuario,
        )


# ─────────────────────────────────────────── Autenticação ────────────────────

class RedirecionamentoSemLoginTest(TestCase):
    """Verifica que as rotas protegidas redirecionam usuários não autenticados."""

    def test_dashboard_redireciona(self):
        response = self.client.get(reverse("financeiro:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_lancamentos_redireciona(self):
        response = self.client.get(reverse("financeiro:lancamento-lista"))
        self.assertEqual(response.status_code, 302)

    def test_relatorio_redireciona(self):
        response = self.client.get(reverse("financeiro:relatorio"))
        self.assertEqual(response.status_code, 302)

    def test_analise_redireciona(self):
        response = self.client.post(reverse("financeiro:analise-financeira"))
        self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────── Dashboard ───────────────────────

class DashboardViewTest(BaseFinanceiroTestCase):
    """Testes da DashboardView."""

    def test_acesso_autenticado_retorna_200(self):
        response = self.client.get(reverse("financeiro:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(reverse("financeiro:dashboard"))
        self.assertTemplateUsed(response, "financeiro/lancamentos/dashboard.html")

    def test_context_contem_saldo(self):
        response = self.client.get(reverse("financeiro:dashboard"))
        self.assertIn("saldo", response.context)
        saldo = response.context["saldo"]
        self.assertIn("receitas", saldo)
        self.assertIn("despesas", saldo)
        self.assertIn("saldo", saldo)

    def test_context_contem_ultimos(self):
        response = self.client.get(reverse("financeiro:dashboard"))
        self.assertIn("ultimos", response.context)

    def test_context_contem_dados_graficos(self):
        response = self.client.get(reverse("financeiro:dashboard"))
        self.assertIn("grafico_meses", response.context)
        self.assertIn("grafico_receitas", response.context)
        self.assertIn("grafico_despesas", response.context)
        self.assertIn("grafico_cat_labels", response.context)


# ─────────────────────────────────────────── Lançamentos ─────────────────────

class LancamentoListViewTest(BaseFinanceiroTestCase):
    """Testes da LancamentoListView."""

    def test_listagem_retorna_200(self):
        response = self.client.get(reverse("financeiro:lancamento-lista"))
        self.assertEqual(response.status_code, 200)

    def test_lista_apenas_proprios_lancamentos(self):
        response = self.client.get(reverse("financeiro:lancamento-lista"))
        qs = response.context["object_list"]
        for l in qs:
            self.assertEqual(l.usuario, self.usuario)

    def test_filtro_tipo_receita(self):
        Lancamento.objects.create(
            descricao="Despesa teste",
            tipo=Lancamento.TIPO_DESPESA,
            valor=Decimal("50.00"),
            data=date.today(),
            categoria=self.categoria,
            usuario=self.usuario,
        )
        response = self.client.get(reverse("financeiro:lancamento-lista"), {"tipo": "receita"})
        qs = response.context["object_list"]
        for l in qs:
            self.assertEqual(l.tipo, Lancamento.TIPO_RECEITA)

    def test_ajax_retorna_partial(self):
        response = self.client.get(
            reverse("financeiro:lancamento-lista"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "financeiro/lancamentos/partials/lancamento_tabela.html",
        )

    def test_nao_ve_lancamentos_de_outro_usuario(self):
        response = self.client.get(reverse("financeiro:lancamento-lista"))
        pks = [l.pk for l in response.context["object_list"]]
        self.assertNotIn(self.outro_lancamento.pk, pks)


class LancamentoCreateViewTest(BaseFinanceiroTestCase):
    """Testes da LancamentoCreateView."""

    def _post_valid(self):
        return self.client.post(
            reverse("financeiro:lancamento-criar"),
            {
                "descricao": "Novo lançamento",
                "tipo": Lancamento.TIPO_RECEITA,
                "valor": "250.00",
                "data": date.today().isoformat(),
                "categoria": self.categoria.pk,
            },
        )

    def test_get_retorna_200(self):
        response = self.client.get(reverse("financeiro:lancamento-criar"))
        self.assertEqual(response.status_code, 200)

    def test_post_valido_cria_lancamento(self):
        total_antes = Lancamento.objects.filter(usuario=self.usuario).count()
        self._post_valid()
        total_depois = Lancamento.objects.filter(usuario=self.usuario).count()
        self.assertEqual(total_depois, total_antes + 1)

    def test_post_valido_redireciona(self):
        response = self._post_valid()
        self.assertRedirects(response, reverse("financeiro:lancamento-lista"))

    def test_lancamento_pertence_ao_usuario_logado(self):
        self._post_valid()
        lancamento = Lancamento.objects.filter(descricao="Novo lançamento").first()
        self.assertIsNotNone(lancamento)
        self.assertEqual(lancamento.usuario, self.usuario)


class LancamentoUpdateViewTest(BaseFinanceiroTestCase):
    """Testes da LancamentoUpdateView."""

    def test_get_retorna_200(self):
        response = self.client.get(
            reverse("financeiro:lancamento-editar", args=[self.lancamento.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_post_atualiza_valor(self):
        self.client.post(
            reverse("financeiro:lancamento-editar", args=[self.lancamento.pk]),
            {
                "descricao": "Salário atualizado",
                "tipo": Lancamento.TIPO_RECEITA,
                "valor": "4500.00",
                "data": date.today().isoformat(),
                "categoria": self.categoria.pk,
            },
        )
        self.lancamento.refresh_from_db()
        self.assertEqual(self.lancamento.valor, Decimal("4500.00"))

    def test_nao_edita_lancamento_de_outro_usuario(self):
        response = self.client.get(
            reverse("financeiro:lancamento-editar", args=[self.outro_lancamento.pk])
        )
        self.assertEqual(response.status_code, 403)


class LancamentoDeleteViewTest(BaseFinanceiroTestCase):
    """Testes da LancamentoDeleteView (AJAX)."""

    def _delete(self, pk, client=None):
        c = client or self.client
        return c.post(
            reverse("financeiro:lancamento-excluir", args=[pk]),
            content_type="application/json",
            HTTP_X_CSRFTOKEN="fake",
        )

    def test_delete_proprio_lancamento(self):
        response = self._delete(self.lancamento.pk)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertFalse(Lancamento.objects.filter(pk=self.lancamento.pk).exists())

    def test_delete_lancamento_alheio_retorna_404(self):
        response = self._delete(self.outro_lancamento.pk)
        data = json.loads(response.content)
        self.assertFalse(data["success"])


# ─────────────────────────────────────────── Categorias ──────────────────────

class CategoriaListViewTest(BaseFinanceiroTestCase):
    """Testes da CategoriaListView."""

    def test_listagem_retorna_200(self):
        response = self.client.get(reverse("financeiro:categoria-lista"))
        self.assertEqual(response.status_code, 200)

    def test_lista_apenas_proprias_categorias(self):
        response = self.client.get(reverse("financeiro:categoria-lista"))
        qs = response.context["object_list"]
        for cat in qs:
            self.assertEqual(cat.usuario, self.usuario)

    def test_nao_ve_categorias_de_outro_usuario(self):
        response = self.client.get(reverse("financeiro:categoria-lista"))
        pks = [c.pk for c in response.context["object_list"]]
        self.assertNotIn(self.outro_categoria.pk, pks)


class CategoriaCreateViewTest(BaseFinanceiroTestCase):
    """Testes da CategoriaCreateView."""

    def test_get_retorna_200(self):
        response = self.client.get(reverse("financeiro:categoria-criar"))
        self.assertEqual(response.status_code, 200)

    def test_post_valido_cria_categoria(self):
        total_antes = Categoria.objects.filter(usuario=self.usuario).count()
        self.client.post(
            reverse("financeiro:categoria-criar"),
            {"nome": "Nova Categoria", "cor": "#123456"},
        )
        total_depois = Categoria.objects.filter(usuario=self.usuario).count()
        self.assertEqual(total_depois, total_antes + 1)

    def test_nome_duplicado_nao_cria(self):
        total_antes = Categoria.objects.filter(usuario=self.usuario).count()
        self.client.post(
            reverse("financeiro:categoria-criar"),
            {"nome": "Alimentação", "cor": "#000000"},
        )
        total_depois = Categoria.objects.filter(usuario=self.usuario).count()
        self.assertEqual(total_antes, total_depois)


class CategoriaUpdateViewTest(BaseFinanceiroTestCase):
    """Testes da CategoriaUpdateView."""

    def test_get_retorna_200(self):
        response = self.client.get(
            reverse("financeiro:categoria-editar", args=[self.categoria.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_post_atualiza_nome(self):
        self.client.post(
            reverse("financeiro:categoria-editar", args=[self.categoria.pk]),
            {"nome": "Alimentação Editada", "cor": "#ffffff"},
        )
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nome, "Alimentação Editada")

    def test_nao_edita_categoria_de_outro_usuario(self):
        response = self.client.get(
            reverse("financeiro:categoria-editar", args=[self.outro_categoria.pk])
        )
        self.assertEqual(response.status_code, 403)


class CategoriaDeleteViewTest(BaseFinanceiroTestCase):
    """Testes da CategoriaDeleteView (AJAX)."""

    def test_delete_propria_categoria_sem_lancamentos(self):
        cat_vazia = Categoria.objects.create(
            nome="Vazia", cor="#aabbcc", usuario=self.usuario
        )
        response = self.client.post(
            reverse("financeiro:categoria-excluir", args=[cat_vazia.pk]),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertFalse(Categoria.objects.filter(pk=cat_vazia.pk).exists())

    def test_delete_categoria_com_lancamentos_retorna_erro(self):
        response = self.client.post(
            reverse("financeiro:categoria-excluir", args=[self.categoria.pk]),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        self.assertTrue(Categoria.objects.filter(pk=self.categoria.pk).exists())

    def test_delete_categoria_alheia_retorna_404(self):
        response = self.client.post(
            reverse("financeiro:categoria-excluir", args=[self.outro_categoria.pk]),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertFalse(data["success"])


# ─────────────────────────────────────────── Relatório ───────────────────────

class RelatorioViewTest(BaseFinanceiroTestCase):
    """Testes da RelatorioView."""

    def test_acesso_retorna_200(self):
        response = self.client.get(reverse("financeiro:relatorio"))
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(reverse("financeiro:relatorio"))
        self.assertTemplateUsed(response, "financeiro/lancamentos/relatorio.html")

    def test_context_contem_lancamentos_e_saldo(self):
        response = self.client.get(reverse("financeiro:relatorio"))
        self.assertIn("lancamentos", response.context)
        self.assertIn("saldo", response.context)

    def test_filtro_tipo_funciona(self):
        response = self.client.get(reverse("financeiro:relatorio"), {"tipo": "receita"})
        for l in response.context["lancamentos"]:
            self.assertEqual(l.tipo, Lancamento.TIPO_RECEITA)

    def test_nao_ve_lancamentos_de_outro_usuario(self):
        response = self.client.get(reverse("financeiro:relatorio"))
        pks = [l.pk for l in response.context["lancamentos"]]
        self.assertNotIn(self.outro_lancamento.pk, pks)


class RelatorioPDFViewTest(BaseFinanceiroTestCase):
    """Testes da RelatorioPDFView."""

    def test_retorna_200_e_content_type_pdf(self):
        response = self.client.get(reverse("financeiro:relatorio-pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_header_content_disposition(self):
        response = self.client.get(reverse("financeiro:relatorio-pdf"))
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(".pdf", response["Content-Disposition"])


# ─────────────────────────────────────────── Análise IA ──────────────────────

class AnaliseFinanceiraViewTest(BaseFinanceiroTestCase):
    """Testes da AnaliseFinanceiraView (AJAX + mock OpenAI)."""

    def _url(self):
        return reverse("financeiro:analise-financeira")

    def test_get_nao_permitido(self):
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)

    @patch("Financeiro.lancamentos.business.http_requests.post")
    @patch("Financeiro.lancamentos.business.decouple_config")
    def test_analise_sucesso(self, mock_config, mock_post):
        mock_config.side_effect = lambda key, **kw: (
            "fake-key" if key == "OPENAI_API_KEY" else kw.get("default", "")
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Análise gerada com sucesso."}}]
        }
        mock_post.return_value = mock_response

        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertIn("analise", data)
        self.assertEqual(data["analise"], "Análise gerada com sucesso.")

    @patch("Financeiro.lancamentos.business.decouple_config")
    def test_analise_sem_api_key(self, mock_config):
        mock_config.side_effect = lambda key, **kw: (
            "" if key == "OPENAI_API_KEY" else kw.get("default", "")
        )
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])

    def test_analise_sem_lancamentos(self):
        Lancamento.objects.filter(usuario=self.usuario).delete()
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])

    @patch("Financeiro.lancamentos.business.http_requests.post")
    @patch("Financeiro.lancamentos.business.decouple_config")
    def test_analise_api_erro_500(self, mock_config, mock_post):
        mock_config.side_effect = lambda key, **kw: (
            "fake-key" if key == "OPENAI_API_KEY" else kw.get("default", "")
        )
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])

    @patch("Financeiro.lancamentos.business.http_requests.post")
    @patch("Financeiro.lancamentos.business.decouple_config")
    def test_analise_timeout(self, mock_config, mock_post):
        import requests as http_requests
        mock_config.side_effect = lambda key, **kw: (
            "fake-key" if key == "OPENAI_API_KEY" else kw.get("default", "")
        )
        mock_post.side_effect = http_requests.Timeout("timeout")

        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])


# ─────────────────────────────────────────── Importação de Planilha ──────────

def _criar_xlsx_em_memoria(linhas):
    """
    Utilitário de teste: cria um workbook .xlsx em memória a partir de uma
    lista de listas. A primeira linha é usada como cabeçalho.

    Retorna um objeto BytesIO pronto para ser passado como request.FILES.
    """
    import io
    import openpyxl
    from django.core.files.uploadedfile import SimpleUploadedFile

    wb = openpyxl.Workbook()
    ws = wb.active
    for row in linhas:
        ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return SimpleUploadedFile(
        "planilha.xlsx",
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


class DownloadModeloPlanilhaViewTest(BaseFinanceiroTestCase):
    """Testes da DownloadModeloPlanilhaView."""

    def test_get_retorna_xlsx(self):
        response = self.client.get(reverse("financeiro:lancamento-modelo"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_content_disposition_attachment(self):
        response = self.client.get(reverse("financeiro:lancamento-modelo"))
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(".xlsx", response["Content-Disposition"])

    def test_requer_login(self):
        self.client.logout()
        response = self.client.get(reverse("financeiro:lancamento-modelo"))
        self.assertEqual(response.status_code, 302)


class ImportarPlanilhaViewTest(BaseFinanceiroTestCase):
    """Testes da ImportarPlanilhaView."""

    URL = "financeiro:lancamento-importar"

    def _post(self, arquivo, client=None):
        c = client or self.client
        return c.post(
            reverse(self.URL),
            {"arquivo": arquivo},
            format="multipart",
        )

    # ── Casos de sucesso ──────────────────────────────────────────────────

    def test_importacao_valida_cria_lancamentos(self):
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["receita", "Salário", "3000.00", date.today().isoformat(), "Alimentação", ""],
            ["despesa", "Mercado", "250.50", date.today().isoformat(), "Alimentação", "obs"],
        ])
        total_antes = Lancamento.objects.filter(usuario=self.usuario).count()
        response = self._post(arquivo)
        data = json.loads(response.content)
        self.assertTrue(data["success"], msg=data.get("error"))
        self.assertEqual(
            Lancamento.objects.filter(usuario=self.usuario).count(),
            total_antes + 2,
        )

    def test_importacao_retorna_resumo_correto(self):
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["receita", "Salário", "3000.00", date.today().isoformat(), "Alimentação", ""],
            ["despesa", "Mercado", "200.00", date.today().isoformat(), "Alimentação", ""],
            ["despesa", "Aluguel", "1000.00", date.today().isoformat(), "Alimentação", ""],
        ])
        response = self._post(arquivo)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        resultado = data["resultado"]
        self.assertEqual(resultado["total"], 3)
        self.assertEqual(resultado["receitas"], 1)
        self.assertEqual(resultado["despesas"], 2)

    def test_categoria_inexistente_criada_automaticamente(self):
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["receita", "Bônus", "500.00", date.today().isoformat(), "Bonificações", ""],
        ])
        self.assertFalse(
            Categoria.objects.filter(nome="Bonificações", usuario=self.usuario).exists()
        )
        response = self._post(arquivo)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertTrue(
            Categoria.objects.filter(nome="Bonificações", usuario=self.usuario).exists()
        )

    def test_categoria_com_acento_diferente_encontra_existente(self):
        """'Alimentacao' (sem acento) deve encontrar a categoria 'Alimentação'."""
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["receita", "Salário", "3000.00", date.today().isoformat(), "Alimentacao", ""],
        ])
        total_cats_antes = Categoria.objects.filter(usuario=self.usuario).count()
        response = self._post(arquivo)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        # Não deve ter criado nova categoria
        self.assertEqual(
            Categoria.objects.filter(usuario=self.usuario).count(),
            total_cats_antes,
        )

    def test_categoria_case_insensitive(self):
        """'ALIMENTAÇÃO' (maiúsculas) deve encontrar a categoria 'Alimentação'."""
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["despesa", "Compras", "80.00", date.today().isoformat(), "ALIMENTAÇÃO", ""],
        ])
        total_cats_antes = Categoria.objects.filter(usuario=self.usuario).count()
        response = self._post(arquivo)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertEqual(
            Categoria.objects.filter(usuario=self.usuario).count(),
            total_cats_antes,
        )

    # ── Casos de erro ─────────────────────────────────────────────────────

    def test_tipo_invalido_retorna_400(self):
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["investimento", "Ação XPTO", "500.00", date.today().isoformat(), "Alimentação", ""],
        ])
        total_antes = Lancamento.objects.filter(usuario=self.usuario).count()
        response = self._post(arquivo)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        # Nenhum lançamento deve ter sido criado (atomicidade)
        self.assertEqual(
            Lancamento.objects.filter(usuario=self.usuario).count(),
            total_antes,
        )

    def test_valor_invalido_cancela_importacao(self):
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["receita", "Salário", "0", date.today().isoformat(), "Alimentação", ""],
        ])
        total_antes = Lancamento.objects.filter(usuario=self.usuario).count()
        response = self._post(arquivo)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        self.assertEqual(
            Lancamento.objects.filter(usuario=self.usuario).count(),
            total_antes,
        )

    def test_atomicidade_erro_na_linha_3_cancela_tudo(self):
        """Se a linha 3 tem erro, as linhas 1 e 2 NÃO devem ser persistidas."""
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["receita", "Linha 1 ok", "100.00", date.today().isoformat(), "Alimentação", ""],
            ["despesa", "Linha 2 ok", "50.00",  date.today().isoformat(), "Alimentação", ""],
            ["invalido", "Linha 3 erro", "80.00", date.today().isoformat(), "Alimentação", ""],
        ])
        total_antes = Lancamento.objects.filter(usuario=self.usuario).count()
        response = self._post(arquivo)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        # Exatamente 0 novos lançamentos
        self.assertEqual(
            Lancamento.objects.filter(usuario=self.usuario).count(),
            total_antes,
        )

    def test_formato_invalido_nao_xlsx(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        arquivo_csv = SimpleUploadedFile(
            "dados.csv", b"tipo,descricao\nreceita,Salario", content_type="text/csv"
        )
        response = self._post(arquivo_csv)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])

    def test_requer_login(self):
        self.client.logout()
        from datetime import date
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["receita", "Salário", "3000.00", date.today().isoformat(), "Alimentação", ""],
        ])
        response = self._post(arquivo)
        self.assertEqual(response.status_code, 302)

    def test_nao_usa_categoria_de_outro_usuario(self):
        """Categoria criada para outro usuário não deve ser reutilizada."""
        from datetime import date
        # "Moradia" exists only for outro_usuario
        arquivo = _criar_xlsx_em_memoria([
            ["tipo", "descricao", "valor", "data", "categoria", "observacao"],
            ["despesa", "Aluguel", "1200.00", date.today().isoformat(), "Moradia", ""],
        ])
        total_cats_antes = Categoria.objects.filter(usuario=self.usuario).count()
        response = self._post(arquivo)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        # Deve ter criado uma nova categoria "Moradia" para o usuario logado
        self.assertEqual(
            Categoria.objects.filter(usuario=self.usuario).count(),
            total_cats_antes + 1,
        )
