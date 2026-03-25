"""
Mixins de composição do sistema.

Permitem que instâncias de Model acessem suas camadas de Business, Helper e Rules
de forma lazy, através de propriedades. Para ativar a camada, basta declarar
o atributo ``*_class`` correspondente no Model.

Exemplo de uso no Model::

    class Lancamento(BasicModel, BusinessModelMixin, HelperModelMixin, RulesModelMixin):
        business_class = LancamentoBusiness
        helper_class = LancamentoHelper
        rules_class = LancamentoRules
        ...

Exemplo de chamada::

    lancamento = Lancamento.objects.get(pk=1)
    lancamento.business.processar()
    lancamento.helper.obter_resumo()
    lancamento.rules.validar_valor()
"""


class BusinessModelMixin:
    """
    Mixin que fornece acesso lazy à camada de Business a partir do Model.

    A ``business_class`` deve ser definida no Model concreto.
    A instância de Business recebe a instância do Model como argumento
    no construtor.
    """

    business_class = None
    _business = None

    def _get_business_class(self):
        """Instancia a camada de Business, validando que ela foi declarada."""
        if not self.business_class:
            raise NotImplementedError(
                f"{self.__class__.__name__} deve definir 'business_class'."
            )
        return self.business_class(self)

    @property
    def business(self):
        """Retorna a instância de Business, criando-a na primeira chamada."""
        if not self._business:
            self._business = self._get_business_class()
        return self._business


class HelperModelMixin:
    """
    Mixin que fornece acesso lazy à camada de Helper a partir do Model.

    A ``helper_class`` deve ser definida no Model concreto.
    A instância de Helper recebe a instância do Model como argumento
    no construtor.
    """

    helper_class = None
    _helper = None

    def _get_helper_class(self):
        """Instancia a camada de Helper, validando que ela foi declarada."""
        if not self.helper_class:
            raise NotImplementedError(
                f"{self.__class__.__name__} deve definir 'helper_class'."
            )
        return self.helper_class(self)

    @property
    def helper(self):
        """Retorna a instância de Helper, criando-a na primeira chamada."""
        if not self._helper:
            self._helper = self._get_helper_class()
        return self._helper


class RulesModelMixin:
    """
    Mixin que fornece acesso lazy à camada de Rules a partir do Model.

    A ``rules_class`` deve ser definida no Model concreto.
    A instância de Rules recebe a instância do Model como argumento
    no construtor.
    """

    rules_class = None
    _rules = None

    def _get_rules_class(self):
        """Instancia a camada de Rules, validando que ela foi declarada."""
        if not self.rules_class:
            raise NotImplementedError(
                f"{self.__class__.__name__} deve definir 'rules_class'."
            )
        return self.rules_class(self)

    @property
    def rules(self):
        """Retorna a instância de Rules, criando-a na primeira chamada."""
        if not self._rules:
            self._rules = self._get_rules_class()
        return self._rules
