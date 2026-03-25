"""
Context processors do projeto.

moeda_context: injeta ``moeda_usuario`` no contexto de todos os templates.
Disponível automaticamente em todos os templates via TEMPLATES.context_processors.
"""
import logging

logger = logging.getLogger(__name__)


def _brl_default():
    """Retorna dados padrão para a moeda BRL."""
    return {
        "codigo": "BRL",
        "simbolo": "R$",
        "taxa": 1.0,
        "taxa_inversa": 1.0,
        "nome": "Real Brasileiro",
    }


def moeda_context(request):
    """
    Injeta a moeda preferida do usuário autenticado no contexto de templates.

    Contexto injetado:
        moeda_usuario: dict com:
          - codigo       : código ISO da moeda (ex: "USD", "BRL")
          - simbolo      : símbolo da moeda (ex: "US$", "R$")
          - taxa         : float — multiplicar valor BRL por taxa para obter valor na moeda
          - taxa_inversa : float — bid (quanto BRL equivale a 1 unidade da moeda)
          - nome         : nome completo da moeda

    Para templates não autenticados ou em caso de falha, injeta os valores BRL.
    """
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {"moeda_usuario": _brl_default()}

    try:
        from Usuario.configuracoes.helpers import PreferenciaUsuarioHelper
        from common.currency_service import obter_cotacoes, obter_simbolo_moeda

        preferencia = PreferenciaUsuarioHelper.obter_preferencia(request.user)
        codigo = preferencia.moeda_preferida if preferencia else "BRL"

        if codigo == "BRL":
            return {"moeda_usuario": _brl_default()}

        # Buscar cotação (usa cache sempre que possível)
        dados = obter_cotacoes()
        taxa = 1.0
        taxa_inversa = 1.0
        nome = codigo

        if dados:
            cotacoes = dados.get("cotacoes", {})
            info = cotacoes.get(codigo)
            if info:
                try:
                    from decimal import Decimal

                    bid = Decimal(str(info["bid"]))
                    if bid > 0:
                        taxa = float(Decimal("1") / bid)
                        taxa_inversa = float(bid)
                except Exception:
                    pass
            nome = dados.get("moedas_disponiveis", {}).get(codigo, codigo)

        return {
            "moeda_usuario": {
                "codigo": codigo,
                "simbolo": obter_simbolo_moeda(codigo),
                "taxa": taxa,
                "taxa_inversa": taxa_inversa,
                "nome": nome,
            }
        }

    except Exception as exc:
        logger.warning("Erro no context processor de moeda: %s", exc)
        return {"moeda_usuario": _brl_default()}
