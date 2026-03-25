"""
Serviço de cotação de moedas — integração com AwesomeAPI.

Responsabilidades:
- Manter cache local em ``data/cotacoes.json`` (TTL: 1 minuto).
- Se o cache não existe ou expirou, consultar a AwesomeAPI e recriar o arquivo.
- Expor funções de conversão e listagem de moedas para o restante do sistema.

Endpoints utilizados:
  - GET https://economia.awesomeapi.com.br/json/available
      Retorna todos os pares disponíveis (ex: {"USDBRL": "Dólar Americano/Real Brasileiro"}).
  - GET https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,...
      Retorna a última cotação dos pares solicitados.

Estrutura do cache (data/cotacoes.json)::

    {
      "ultima_atualizacao": "2026-03-25T10:30:00.123456",
      "moedas_disponiveis": {"USD": "Dólar Americano", "EUR": "Euro", ...},
      "cotacoes": {
        "USD": {"nome": "Dólar Americano", "bid": "5.1234"},
        ...
      }
    }
"""
import json
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

CACHE_TTL_SEGUNDOS = 60

AWESOMEAPI_AVAILABLE_URL = "https://economia.awesomeapi.com.br/json/available"
AWESOMEAPI_LAST_URL = "https://economia.awesomeapi.com.br/json/last/{}"

# Mapa de símbolos monetários conhecidos
SIMBOLOS_MOEDAS = {
    "BRL": "R$",
    "USD": "US$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CNY": "¥",
    "CHF": "Fr",
    "AUD": "A$",
    "CAD": "C$",
    "ARS": "$",
    "CLP": "$",
    "COP": "$",
    "MXN": "$",
    "PEN": "S/",
    "UYU": "$U",
    "BOB": "Bs",
    "PYG": "₲",
    "BTC": "₿",
    "ETH": "Ξ",
    "LTC": "Ł",
    "XRP": "XRP",
}


# ─── Funções internas de cache ────────────────────────────────────────────────

def _get_cache_path():
    """Retorna o caminho do arquivo de cache, criando o diretório se necessário."""
    from django.conf import settings

    cache_dir = settings.BASE_DIR / "data"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / "cotacoes.json"


def _is_cache_valido(dados):
    """Verifica se os dados do cache estão dentro do TTL."""
    if not dados or "ultima_atualizacao" not in dados:
        return False
    try:
        ultima = datetime.fromisoformat(dados["ultima_atualizacao"])
        return (datetime.now() - ultima).total_seconds() < CACHE_TTL_SEGUNDOS
    except Exception:
        return False


def _ler_cache():
    """Lê o arquivo de cache. Retorna None se não existir ou estiver corrompido."""
    try:
        path = _get_cache_path()
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _salvar_cache(dados):
    """Persiste os dados no arquivo de cache JSON."""
    try:
        path = _get_cache_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("Erro ao salvar cache de cotações: %s", exc)


# ─── Integração com a API ─────────────────────────────────────────────────────

def _buscar_dados_api():
    """
    Consulta a AwesomeAPI e retorna os dados estruturados para o cache.

    Retorna None em caso de falha (rede indisponível, timeout, erro HTTP).
    """
    try:
        import requests
    except ImportError:
        logger.error("Biblioteca 'requests' não instalada. Execute: pip install requests")
        return None

    try:
        # 1) Buscar todos os pares disponíveis
        resp = requests.get(AWESOMEAPI_AVAILABLE_URL, timeout=10)
        resp.raise_for_status()
        pares = resp.json()

        # Filtrar pares X→BRL (chaves terminando em "BRL", com código de origem != BRL)
        codigos = []
        nomes_raw = {}
        for chave, nome in pares.items():
            if chave.endswith("BRL"):
                codigo_from = chave[:-3]
                if codigo_from and codigo_from != "BRL":
                    codigos.append(codigo_from)
                    nomes_raw[codigo_from] = nome

        if not codigos:
            logger.warning("Nenhum par X-BRL encontrado na AwesomeAPI.")
            return None

        # 2) Buscar cotações em lotes (AwesomeAPI aceita múltiplos pares por request)
        cotacoes = {}
        batch_size = 40
        for i in range(0, len(codigos), batch_size):
            batch = codigos[i : i + batch_size]
            pares_str = ",".join(f"{c}-BRL" for c in batch)
            resp2 = requests.get(AWESOMEAPI_LAST_URL.format(pares_str), timeout=15)
            resp2.raise_for_status()
            data = resp2.json()
            for chave_res, info in data.items():
                # "USDBRL" → "USD"
                codigo = chave_res[:-3] if chave_res.endswith("BRL") else chave_res[:3]
                nome_raw = nomes_raw.get(codigo, info.get("name", codigo))
                nome_limpo = nome_raw.split("/")[0].strip() if "/" in nome_raw else nome_raw
                cotacoes[codigo] = {
                    "nome": nome_limpo,
                    "bid": str(info.get("bid", "1")),
                }

        moedas_disponiveis = {c: cotacoes[c]["nome"] for c in cotacoes}
        return {
            "ultima_atualizacao": datetime.now().isoformat(),
            "moedas_disponiveis": moedas_disponiveis,
            "cotacoes": cotacoes,
        }

    except Exception as exc:
        logger.error("Erro ao consultar AwesomeAPI: %s", exc)
        return None


# ─── API pública do serviço ───────────────────────────────────────────────────

def obter_cotacoes():
    """
    Retorna os dados de cotação do cache ou da API.

    Fluxo:
    1. Lê o arquivo de cache.
    2. Se o cache é válido (< 1 min), retorna-o.
    3. Caso contrário, consulta a AwesomeAPI, atualiza o cache e retorna.
    4. Se a API falhar e houver cache antigo, usa o cache desatualizado.
    5. Se não há cache e a API falhou, retorna None.
    """
    dados = _ler_cache()
    if _is_cache_valido(dados):
        return dados

    novos_dados = _buscar_dados_api()
    if novos_dados:
        _salvar_cache(novos_dados)
        return novos_dados

    # API indisponível: usar cache antigo se existir
    if dados:
        logger.warning("AwesomeAPI indisponível; usando cache desatualizado.")
        return dados

    return None


def obter_moedas_disponiveis():
    """
    Retorna dict {codigo: nome} das moedas disponíveis para conversão.

    Não inclui BRL (moeda base do sistema).
    Retorna {} se a API e o cache estiverem indisponíveis.
    """
    dados = obter_cotacoes()
    if dados:
        return dados.get("moedas_disponiveis", {})
    return {}


def obter_taxa_para_moeda(codigo_moeda):
    """
    Retorna a taxa de conversão de BRL para a moeda alvo como float.

    Taxa = 1 / bid
    Exemplos:
      - BRL         → 1.0
      - USD bid=5.11 → 0.1957...
      - API falhou  → 1.0 (exibe como BRL como fallback seguro)

    O valor pode ser usado diretamente:  valor_moeda = valor_brl * taxa
    """
    if codigo_moeda == "BRL":
        return 1.0

    dados = obter_cotacoes()
    if not dados:
        return 1.0

    info = dados.get("cotacoes", {}).get(codigo_moeda)
    if not info:
        return 1.0

    try:
        bid = Decimal(str(info["bid"]))
        if bid <= 0:
            return 1.0
        return float(Decimal("1") / bid)
    except (InvalidOperation, KeyError, ZeroDivisionError):
        return 1.0


def converter_valor(valor_brl, codigo_moeda):
    """
    Converte um valor em BRL para a moeda alvo.

    Retorna Decimal com 2 casas decimais.
    """
    if codigo_moeda == "BRL":
        return Decimal(str(valor_brl))
    taxa = obter_taxa_para_moeda(codigo_moeda)
    return (Decimal(str(valor_brl)) * Decimal(str(taxa))).quantize(Decimal("0.01"))


def obter_simbolo_moeda(codigo_moeda):
    """Retorna o símbolo da moeda (ex: USD → US$). Padrão: o próprio código."""
    return SIMBOLOS_MOEDAS.get(codigo_moeda, codigo_moeda)
