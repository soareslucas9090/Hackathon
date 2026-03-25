"""
Camada de Business do módulo Financeiro.

Responsabilidade: orquestrar regras de negócio e persistência.
- Chama a camada de Rules antes de salvar.
- Executa as operações dentro de ``transaction.atomic()``.
- Exceções conhecidas (BusinessRulesExceptions, ProcessException) são relançadas.
- Exceções desconhecidas são encapsuladas em SystemErrorException.
"""
from django.db import transaction

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
                "Erro inesperado ao criar categoria."
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
                "Erro inesperado ao atualizar categoria."
            ) from exc

    def excluir(self):
        """Remove a Categoria se ela não possuir lançamentos vinculados."""
        try:
            with transaction.atomic():
                if self.model_instance.lancamentos.exists():
                    raise ProcessException(
                        "Não é possível excluir uma categoria que possui lançamentos."
                    )
                self.model_instance.delete()
        except (BusinessRulesExceptions, ProcessException):
            raise
        except Exception as exc:
            raise SystemErrorException(
                "Erro inesperado ao excluir categoria."
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
                "Erro inesperado ao criar lançamento."
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
                "Erro inesperado ao atualizar lançamento."
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
                "Erro inesperado ao excluir lançamento."
            ) from exc
