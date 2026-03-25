"""
Camada de Rules do módulo Financeiro.

Responsabilidade: validar regras de negócio.
- Retorna ``False`` quando nenhuma regra é violada.
- Lança ``BusinessRulesExceptions`` quando uma regra é violada.
- Deve ser chamada exclusivamente pela camada de Business.
"""
from django.utils.translation import gettext as _

from core.exceptions import BusinessRulesExceptions
from core.mixins import ModelRules


class CategoriaRules(ModelRules):
    """Regras de negócio da Categoria."""

    def validar_nome_unico(self):
        """
        Valida que o nome da categoria não está duplicado para o mesmo usuário.

        Considera o campo ``pk`` para ignorar o próprio registro em edições.
        """
        from .models import Categoria

        qs = Categoria.objects.filter(
            nome__iexact=self.model_instance.nome,
            usuario=self.model_instance.usuario,
        )
        if self.model_instance.pk:
            qs = qs.exclude(pk=self.model_instance.pk)

        if qs.exists():
            raise BusinessRulesExceptions(
                _("Já existe uma categoria com o nome '%(nome)s'.")
                % {"nome": self.model_instance.nome}
            )
        return False


class LancamentoRules(ModelRules):
    """Regras de negócio do Lançamento."""

    def validar_valor(self):
        """Valida que o valor do lançamento é positivo."""
        if self.model_instance.valor is None or self.model_instance.valor <= 0:
            raise BusinessRulesExceptions(
                _("O valor do lançamento deve ser maior que zero.")
            )
        return False

    def validar_categoria_do_usuario(self):
        """Valida que a categoria pertence ao mesmo usuário do lançamento."""
        if (
            self.model_instance.categoria_id
            and hasattr(self.model_instance, "categoria")
            and self.model_instance.categoria.usuario_id != self.model_instance.usuario_id
        ):
            raise BusinessRulesExceptions(
                _("A categoria selecionada não pertence ao seu usuário.")
            )
        return False
