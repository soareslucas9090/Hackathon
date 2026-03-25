"""
Exceções personalizadas do sistema.

Hierarquia de exceções:
- BusinessRulesExceptions: lançada pela camada de Rules quando uma regra de negócio é violada.
- ProcessException: lançada pela camada de Business para erros de processamento tratados.
- SystemErrorException: lançada pela camada de Business para erros inesperados do sistema.
"""


class BusinessRulesExceptions(Exception):
    """
    Exceção lançada pela camada de Rules quando uma regra de negócio é violada.

    Deve ser capturada pela camada de Business e repassada à View,
    que por sua vez retornará uma resposta HTTP 400 ao cliente.

    Exemplo de uso::

        class MinhaRule:
            def validar_saldo(self, valor):
                if valor < 0:
                    raise BusinessRulesExceptions("Saldo não pode ser negativo.")
                return False
    """

    def __init__(self, message: str = "Regra de negócio violada."):
        self.message = message
        super().__init__(self.message)


class ProcessException(Exception):
    """
    Exceção lançada pela camada de Business para erros de processamento tratados.

    Representa um estado de erro esperado e mapeado (ex.: dado duplicado,
    operação não permitida no momento). A View retornará HTTP 400 ao cliente.

    Exemplo de uso::

        class MeuBusiness:
            def criar_lancamento(self, dados):
                try:
                    ...
                except AlgumErroConhecido as e:
                    raise ProcessException(str(e)) from e
    """

    def __init__(self, message: str = "Erro no processamento da operação."):
        self.message = message
        super().__init__(self.message)


class SystemErrorException(Exception):
    """
    Exceção lançada pela camada de Business para erros inesperados do sistema.

    Representa falhas não previstas que exigem análise de suporte.
    A View retornará HTTP 500 ao cliente.

    Exemplo de uso::

        class MeuBusiness:
            def criar_lancamento(self, dados):
                try:
                    ...
                except Exception as e:
                    raise SystemErrorException(str(e)) from e
    """

    def __init__(self, message: str = "Erro inesperado no sistema. Contate o suporte."):
        self.message = message
        super().__init__(self.message)
