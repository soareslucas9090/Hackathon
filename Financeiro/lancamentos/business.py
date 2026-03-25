"""
Camada de Business do módulo Financeiro.

Responsabilidade: orquestrar regras de negócio e persistência.
- Chama a camada de Rules antes de salvar.
- Executa as operações dentro de ``transaction.atomic()``.
- Exceções conhecidas (BusinessRulesExceptions, ProcessException) são relançadas.
- Exceções desconhecidas são encapsuladas em SystemErrorException.
"""
from django.db import transaction
from django.utils.translation import gettext as _

from core.exceptions import BusinessRulesExceptions, ProcessException, SystemErrorException
from core.mixins import ModelBusiness


class CategoriaBusiness(ModelBusiness):
    """Business de Categoria."""

    def criar(self):
        """Valida e persiste uma nova Categoria."""
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_nome_unico()
                self.model_instance.save()
                return self.model_instance
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                _("Erro inesperado ao criar categoria.")
            ) from exc

    def atualizar(self):
        """Valida e atualiza a Categoria existente."""
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_nome_unico()
                self.model_instance.save()
                return self.model_instance
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                _("Erro inesperado ao atualizar categoria.")
            ) from exc

    def excluir(self):
        """Remove a Categoria se ela não possuir lançamentos vinculados."""
        try:
            with transaction.atomic():
                if self.model_instance.lancamentos.exists():
                    raise ProcessException(
                        _("Não é possível excluir uma categoria que possui lançamentos.")
                    )
                self.model_instance.delete()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                _("Erro inesperado ao excluir categoria.")
            ) from exc


class LancamentoBusiness(ModelBusiness):
    """Business de Lançamento."""

    def criar(self):
        """Valida e persiste um novo Lançamento."""
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_valor()
                self.model_instance.rules.validar_categoria_do_usuario()
                self.model_instance.save()
                return self.model_instance
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                _("Erro inesperado ao criar lançamento.")
            ) from exc

    def atualizar(self):
        """Valida e atualiza o Lançamento existente."""
        try:
            with transaction.atomic():
                self.model_instance.rules.validar_valor()
                self.model_instance.rules.validar_categoria_do_usuario()
                self.model_instance.save()
                return self.model_instance
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                _("Erro inesperado ao atualizar lançamento.")
            ) from exc

    def excluir(self):
        """Remove o Lançamento."""
        try:
            with transaction.atomic():
                self.model_instance.delete()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                _("Erro inesperado ao excluir lançamento.")
            ) from exc

    def gerar_analise_financeira(self):
        """Valida dados, monta prompt e solicita análise à API OpenAI."""
        import logging
        from decouple import config as decouple_config
        import requests as http_requests

        logger = logging.getLogger(__name__)

        try:
            self.model_instance.rules.validar_possui_lancamentos()

            dados = self.model_instance.helper.obter_lancamentos_periodo(meses=3)

            receitas_txt = "\n".join(dados["receitas"]) or "Nenhuma receita registrada."
            despesas_txt = "\n".join(dados["despesas"]) or "Nenhuma despesa registrada."

            prompt = (
                "Você é um consultor financeiro pessoal. Analise os dados financeiros "
                "abaixo dos últimos 3 meses e forneça:\n\n"
                "1. **Maiores gastos**: identifique as categorias e itens com maiores despesas.\n"
                "2. **Projeção para 1 mês à frente**: expectativa de receitas e despesas.\n"
                "3. **Projeção para 3 meses à frente**: expectativa de receitas e despesas.\n"
                "4. **Projeção para 1 ano à frente**: expectativa de receitas e despesas.\n"
                "5. **Recomendações**: sugestões práticas para melhorar a saúde financeira.\n\n"
                "Seja realista e objetivo. Use os dados reais fornecidos.\n\n"
                f"--- RECEITAS ---\n{receitas_txt}\n\n"
                f"--- DESPESAS ---\n{despesas_txt}"
            )

            api_key = decouple_config("OPENAI_API_KEY", default="")
            if not api_key:
                raise ProcessException(
                    _("Chave da API OpenAI não configurada. Configure OPENAI_API_KEY no .env.")
                )

            response = http_requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": decouple_config("OPENAI_MODEL", default="gpt-4o-mini"),
                    "messages": [
                        {"role": "system", "content": "Você é um consultor financeiro pessoal experiente."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                timeout=60,
            )

            if response.status_code != 200:
                logger.error(
                    "Erro na API OpenAI: status=%s body=%s",
                    response.status_code,
                    response.text[:500],
                )
                raise ProcessException(
                    _("Não foi possível obter a análise. Tente novamente mais tarde.")
                )

            resultado = response.json()
            analise = (
                resultado.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            if not analise:
                raise ProcessException(
                    _("A API retornou uma resposta vazia. Tente novamente.")
                )

            return analise

        except (BusinessRulesExceptions, ProcessException):
            raise
        except http_requests.Timeout:
            raise ProcessException(
                _("A análise demorou demais. Tente novamente em alguns instantes.")
            )
        except http_requests.ConnectionError:
            raise ProcessException(
                _("Erro de conexão com o serviço de análise. Verifique sua internet.")
            )
        except Exception as exc:
            raise SystemErrorException(
                _("Erro inesperado ao gerar análise financeira.")
            ) from exc
