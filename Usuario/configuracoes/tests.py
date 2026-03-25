"""
Testes automatizados do módulo de configurações de usuário.

Cobertura:
- ConfiguracaoMoedaView (GET e POST)
- Redirecionamento sem login
- Isolamento de dados entre usuários
- PreferenciaUsuarioHelper (get_or_create)
- PreferenciaUsuarioBusiness (atualizar_moeda)
- PreferenciaUsuarioRules (validar_moeda_disponivel)
- currency_service (cache, conversão, fallback)

Execução::

    python manage.py test Usuario.configuracoes.tests
"""
import json
import os
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import PreferenciaUsuario

User = get_user_model()


# ─────────────────────────── Base ────────────────────────────────────────────

class BaseConfiguracaoTestCase(TestCase):
    """Caso de teste base com usuário autenticado e preferência padrão BRL."""

    def setUp(self):
        self.client = Client()
        self.client2 = Client()

        self.usuario = User.objects.create_user(
            username="config_user", password="senha123"
        )
        self.outro_usuario = User.objects.create_user(
            username="outro_config", password="senha123"
        )

        self.client.force_login(self.usuario)
        self.client2.force_login(self.outro_usuario)

        self.preferencia = PreferenciaUsuario.objects.create(
            usuario=self.usuario, moeda_preferida="BRL"
        )
        self.outra_preferencia = PreferenciaUsuario.objects.create(
            usuario=self.outro_usuario, moeda_preferida="BRL"
        )


# ─────────────────────────── Autenticação ─────────────────────────────────────

class RedirecionamentoSemLoginConfiguracaoTest(TestCase):
    """Garante que a view de configuração redireciona usuários não autenticados."""

    def test_configuracao_moeda_redireciona_sem_login(self):
        response = self.client.get(reverse("configuracoes:moeda"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])


# ─────────────────────────── ConfiguracaoMoedaView ───────────────────────────

class ConfiguracaoMoedaViewGetTest(BaseConfiguracaoTestCase):
    """Testes da ConfiguracaoMoedaView — método GET."""

    @patch("common.currency_service._buscar_dados_api")
    def test_get_retorna_200(self, mock_api):
        mock_api.return_value = None
        response = self.client.get(reverse("configuracoes:moeda"))
        self.assertEqual(response.status_code, 200)

    @patch("common.currency_service._buscar_dados_api")
    def test_get_usa_template_correto(self, mock_api):
        mock_api.return_value = None
        response = self.client.get(reverse("configuracoes:moeda"))
        self.assertTemplateUsed(response, "usuario/configuracoes/configuracao_moeda.html")

    @patch("common.currency_service._buscar_dados_api")
    def test_get_contem_form_no_contexto(self, mock_api):
        mock_api.return_value = None
        response = self.client.get(reverse("configuracoes:moeda"))
        self.assertIn("form", response.context)

    @patch("common.currency_service._buscar_dados_api")
    def test_get_page_title_correto(self, mock_api):
        mock_api.return_value = None
        response = self.client.get(reverse("configuracoes:moeda"))
        self.assertEqual(response.context["page_title"], "Configurações de Moeda")


class ConfiguracaoMoedaViewPostTest(BaseConfiguracaoTestCase):
    """Testes da ConfiguracaoMoedaView — método POST."""

    @patch("common.currency_service._buscar_dados_api")
    def test_post_brl_salva_com_sucesso(self, mock_api):
        mock_api.return_value = None
        self.preferencia.moeda_preferida = "USD"
        self.preferencia.save()

        response = self.client.post(
            reverse("configuracoes:moeda"),
            {"moeda_preferida": "BRL"},
        )
        self.assertEqual(response.status_code, 302)
        self.preferencia.refresh_from_db()
        self.assertEqual(self.preferencia.moeda_preferida, "BRL")

    @patch("common.currency_service.obter_moedas_disponiveis")
    def test_post_usd_com_api_disponivel(self, mock_moedas):
        mock_moedas.return_value = {"USD": "Dólar Americano", "EUR": "Euro"}

        response = self.client.post(
            reverse("configuracoes:moeda"),
            {"moeda_preferida": "USD"},
        )
        self.assertEqual(response.status_code, 302)
        self.preferencia.refresh_from_db()
        self.assertEqual(self.preferencia.moeda_preferida, "USD")

    @patch("common.currency_service.obter_moedas_disponiveis")
    def test_post_moeda_invalida_nao_salva(self, mock_moedas):
        mock_moedas.return_value = {"USD": "Dólar Americano", "EUR": "Euro"}

        response = self.client.post(
            reverse("configuracoes:moeda"),
            {"moeda_preferida": "XYZ"},
        )
        # Deve retornar 400 (BusinessRulesExceptions → ExceptionHandlerMixin)
        self.assertEqual(response.status_code, 400)
        self.preferencia.refresh_from_db()
        self.assertNotEqual(self.preferencia.moeda_preferida, "XYZ")

    @patch("common.currency_service._buscar_dados_api")
    def test_post_redireciona_para_propria_pagina(self, mock_api):
        mock_api.return_value = None
        response = self.client.post(
            reverse("configuracoes:moeda"),
            {"moeda_preferida": "BRL"},
        )
        self.assertRedirects(response, reverse("configuracoes:moeda"))


# ─────────────────────────── Isolamento de dados ─────────────────────────────

class IsolamentoDadosConfiguracaoTest(BaseConfiguracaoTestCase):
    """Garante que um usuário não modifica a preferência de outro."""

    @patch("common.currency_service.obter_moedas_disponiveis")
    def test_post_modifica_apenas_usuario_logado(self, mock_moedas):
        mock_moedas.return_value = {"USD": "Dólar Americano"}

        self.client.post(
            reverse("configuracoes:moeda"),
            {"moeda_preferida": "USD"},
        )

        self.preferencia.refresh_from_db()
        self.outra_preferencia.refresh_from_db()
        self.assertEqual(self.preferencia.moeda_preferida, "USD")
        self.assertEqual(self.outra_preferencia.moeda_preferida, "BRL")


# ─────────────────────────── Helper ──────────────────────────────────────────

class PreferenciaUsuarioHelperTest(TestCase):
    """Testes de PreferenciaUsuarioHelper."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="helper_user", password="senha123"
        )

    def test_cria_preferencia_se_nao_existir(self):
        self.assertFalse(PreferenciaUsuario.objects.filter(usuario=self.usuario).exists())
        pref = PreferenciaUsuario(usuario=self.usuario).helper.obter_preferencia()
        self.assertIsNotNone(pref)
        self.assertEqual(pref.moeda_preferida, "BRL")
        self.assertTrue(PreferenciaUsuario.objects.filter(usuario=self.usuario).exists())

    def test_retorna_existente_sem_duplicar(self):
        PreferenciaUsuario.objects.create(usuario=self.usuario, moeda_preferida="EUR")
        pref = PreferenciaUsuario(usuario=self.usuario).helper.obter_preferencia()
        self.assertEqual(pref.moeda_preferida, "EUR")
        self.assertEqual(PreferenciaUsuario.objects.filter(usuario=self.usuario).count(), 1)


# ─────────────────────────── Rules ───────────────────────────────────────────

class PreferenciaUsuarioRulesTest(TestCase):
    """Testes de PreferenciaUsuarioRules."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="rules_user", password="senha123"
        )
        self.preferencia = PreferenciaUsuario.objects.create(
            usuario=self.usuario, moeda_preferida="BRL"
        )

    def test_brl_sempre_valido(self):
        from core.exceptions import BusinessRulesExceptions

        self.preferencia.moeda_preferida = "BRL"
        # Não deve lançar exceção
        self.preferencia.rules.validar_moeda_disponivel()

    @patch("common.currency_service.obter_moedas_disponiveis")
    def test_moeda_valida_na_api(self, mock_moedas):
        mock_moedas.return_value = {"USD": "Dólar Americano"}
        self.preferencia.moeda_preferida = "USD"
        # Não deve lançar exceção
        self.preferencia.rules.validar_moeda_disponivel()

    @patch("common.currency_service.obter_moedas_disponiveis")
    def test_moeda_invalida_lanca_excecao(self, mock_moedas):
        from core.exceptions import BusinessRulesExceptions

        mock_moedas.return_value = {"USD": "Dólar Americano"}
        self.preferencia.moeda_preferida = "XYZ"
        with self.assertRaises(BusinessRulesExceptions):
            self.preferencia.rules.validar_moeda_disponivel()

    @patch("common.currency_service.obter_moedas_disponiveis")
    def test_api_indisponivel_aceita_qualquer_codigo(self, mock_moedas):
        """Se a API retornar vazio, não deve bloquear a atualização."""
        mock_moedas.return_value = {}
        self.preferencia.moeda_preferida = "USD"
        # Não deve lançar exceção quando API retorna vazio
        self.preferencia.rules.validar_moeda_disponivel()

    def test_moeda_vazia_lanca_excecao(self):
        from core.exceptions import BusinessRulesExceptions

        self.preferencia.moeda_preferida = ""
        with self.assertRaises(BusinessRulesExceptions):
            self.preferencia.rules.validar_moeda_disponivel()


# ─────────────────────────── CurrencyService ─────────────────────────────────

class CurrencyServiceTest(TestCase):
    """Testes unitários do serviço de cotação de moedas."""

    def _make_api_response(self):
        """Dados simulados de resposta da AwesomeAPI."""
        return {
            "ultima_atualizacao": datetime.now().isoformat(),
            "moedas_disponiveis": {"USD": "Dólar Americano", "EUR": "Euro"},
            "cotacoes": {
                "USD": {"nome": "Dólar Americano", "bid": "5.1000"},
                "EUR": {"nome": "Euro", "bid": "5.6000"},
            },
        }

    @patch("common.currency_service._buscar_dados_api")
    def test_obter_cotacoes_chama_api_quando_sem_cache(self, mock_api):
        from common.currency_service import obter_cotacoes

        mock_api.return_value = self._make_api_response()

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("common.currency_service._get_cache_path") as mock_path:
                from pathlib import Path
                mock_path.return_value = Path(tmpdir) / "cotacoes.json"
                dados = obter_cotacoes()

        mock_api.assert_called_once()
        self.assertIsNotNone(dados)
        self.assertIn("cotacoes", dados)

    @patch("common.currency_service._buscar_dados_api")
    def test_obter_cotacoes_usa_cache_valido(self, mock_api):
        from common.currency_service import obter_cotacoes

        cache_valido = self._make_api_response()

        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path
            cache_file = Path(tmpdir) / "cotacoes.json"
            with open(cache_file, "w") as f:
                json.dump(cache_valido, f)

            with patch("common.currency_service._get_cache_path") as mock_path:
                mock_path.return_value = cache_file
                obter_cotacoes()  # deve usar cache, não chamar API

        mock_api.assert_not_called()

    @patch("common.currency_service._buscar_dados_api")
    def test_obter_cotacoes_renova_cache_expirado(self, mock_api):
        from common.currency_service import obter_cotacoes

        cache_expirado = self._make_api_response()
        cache_expirado["ultima_atualizacao"] = (
            datetime.now() - timedelta(seconds=120)
        ).isoformat()
        mock_api.return_value = self._make_api_response()

        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path
            cache_file = Path(tmpdir) / "cotacoes.json"
            with open(cache_file, "w") as f:
                json.dump(cache_expirado, f)

            with patch("common.currency_service._get_cache_path") as mock_path:
                mock_path.return_value = cache_file
                obter_cotacoes()

        mock_api.assert_called_once()

    @patch("common.currency_service.obter_cotacoes")
    def test_obter_taxa_para_moeda_brl_retorna_1(self, mock_cotacoes):
        from common.currency_service import obter_taxa_para_moeda

        taxa = obter_taxa_para_moeda("BRL")
        self.assertEqual(taxa, 1.0)
        mock_cotacoes.assert_not_called()

    @patch("common.currency_service.obter_cotacoes")
    def test_obter_taxa_para_moeda_usd(self, mock_cotacoes):
        from common.currency_service import obter_taxa_para_moeda

        mock_cotacoes.return_value = self._make_api_response()
        taxa = obter_taxa_para_moeda("USD")
        # bid = 5.10, taxa = 1/5.10 ≈ 0.1960...
        expected = 1.0 / 5.1
        self.assertAlmostEqual(taxa, expected, places=4)

    @patch("common.currency_service.obter_cotacoes")
    def test_obter_taxa_api_indisponivel_retorna_1(self, mock_cotacoes):
        from common.currency_service import obter_taxa_para_moeda

        mock_cotacoes.return_value = None
        taxa = obter_taxa_para_moeda("USD")
        self.assertEqual(taxa, 1.0)

    @patch("common.currency_service.obter_taxa_para_moeda")
    def test_converter_valor_brl_sem_conversao(self, mock_taxa):
        from common.currency_service import converter_valor

        resultado = converter_valor(Decimal("1000.00"), "BRL")
        self.assertEqual(resultado, Decimal("1000.00"))
        mock_taxa.assert_not_called()

    @patch("common.currency_service.obter_taxa_para_moeda")
    def test_converter_valor_usd(self, mock_taxa):
        from common.currency_service import converter_valor

        mock_taxa.return_value = 0.2  # 1 BRL = 0.20 USD
        resultado = converter_valor(Decimal("100.00"), "USD")
        self.assertEqual(resultado, Decimal("20.00"))

    def test_obter_simbolo_moeda_conhecido(self):
        from common.currency_service import obter_simbolo_moeda

        self.assertEqual(obter_simbolo_moeda("BRL"), "R$")
        self.assertEqual(obter_simbolo_moeda("USD"), "US$")
        self.assertEqual(obter_simbolo_moeda("EUR"), "€")

    def test_obter_simbolo_moeda_desconhecido(self):
        from common.currency_service import obter_simbolo_moeda

        self.assertEqual(obter_simbolo_moeda("XYZ"), "XYZ")


# ─────────────────────────── Template filter ─────────────────────────────────

class ConverterMoedaFilterTest(TestCase):
    """Testes do template filter converter_moeda."""

    def test_conversao_basica(self):
        from common.templatetags.moeda_tags import converter_moeda

        resultado = converter_moeda(Decimal("1000.00"), 0.2)
        self.assertEqual(resultado, Decimal("200.00"))

    def test_taxa_1_retorna_mesmo_valor(self):
        from common.templatetags.moeda_tags import converter_moeda

        resultado = converter_moeda(Decimal("3000.00"), 1.0)
        self.assertEqual(resultado, Decimal("3000.00"))

    def test_valor_invalido_retorna_original(self):
        from common.templatetags.moeda_tags import converter_moeda

        resultado = converter_moeda("invalido", 1.0)
        self.assertEqual(resultado, "invalido")

    def test_precisao_duas_casas(self):
        from common.templatetags.moeda_tags import converter_moeda

        resultado = converter_moeda(Decimal("100.00"), 1 / 3)
        # Deve ter exatamente 2 casas decimais
        self.assertEqual(resultado, Decimal("33.33"))
