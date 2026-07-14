"""Acesso centralizado aos dados locais (CSV) e às constantes compartilhadas pelas views."""
import unicodedata
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "data" / "paises.csv"

# Nomes dos países monitorados localmente → sigla ISO2 (usada pelo flagcdn e World Bank)
MAPA_SIGLAS = {
    "Brasil": "br", "Estados Unidos": "us", "China": "cn",
    "Alemanha": "de", "Índia": "in", "Japão": "jp",
    "Canadá": "ca", "França": "fr", "Reino Unido": "gb",
    "Austrália": "au"
}

# Indicadores disponíveis no sistema
INDICADORES_DISPONIVEIS = [
    {"valor": "pib", "label": "PIB"},
    {"valor": "idh", "label": "IDH"},
    {"valor": "inflacao", "label": "Inflação"},
    {"valor": "estabilidade", "label": "Estabilidade"},
    {"valor": "pib_per_capita", "label": "PIB per Capita"},
    {"valor": "gastos_militares", "label": "Gastos Militares (% PIB)"},
    {"valor": "divida_publica", "label": "Dívida Pública (% PIB)"},
    {"valor": "gini", "label": "Índice de Gini"},
    {"valor": "indice_democracia", "label": "Índice de Democracia"},
]

# Colunas numéricas válidas para ordenação
COLUNAS_ORDENACAO = [
    "pib", "idh", "inflacao", "estabilidade",
    "pib_per_capita", "gastos_militares", "divida_publica",
    "gini", "indice_democracia"
]

# Códigos da API World Bank para indicadores
CODIGOS_API_WB = {
    "inflacao": "FP.CPI.TOTL.ZG",
    "pib": "NY.GDP.MKTP.CD",
    "pib_per_capita": "NY.GDP.PCAP.PP.CD",
}


def carregar_dados():
    """Lê o CSV de países e devolve um DataFrame."""
    return pd.read_csv(CSV_PATH)


def get_dado_recente(historico, divisor=1):
    """Extrai o valor mais recente (não nulo) de uma resposta do World Bank."""
    if historico:
        for registro in historico:
            if registro.get('value') is not None:
                return round(registro['value'] / divisor, 2)
    return None


def get_sigla_iso2(nome_pais):
    """Retorna a sigla ISO2 de um país."""
    return MAPA_SIGLAS.get(nome_pais, "")


def validar_indicador(indicador, padrao="pib"):
    """Valida e retorna um indicador válido para ordenação."""
    if indicador in COLUNAS_ORDENACAO:
        return indicador
    return padrao


def _normalizar(texto):
    """Remove acentos e caixa para comparar aliases (ex.: 'Índia' == 'india' == 'INDIA')."""
    if not texto:
        return ""
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().lower()


def resolver_pais(query):
    """
    Resolve um termo (nome local em português, nome em inglês da API do World Bank ou
    código ISO2) para um único objeto canônico de país — a mesma entidade, não importa
    o alias ou o idioma usado para chegar nela (ex.: "Brasil", "BR", "brasil" e "Brazil"
    resolvem todos para o mesmo país local).

    Retorna um dict {"id": "BR", "nome": "Brasil", "iso2": "br", "fonte": "local"|"global"}
    ou None se nenhum alias local/global corresponder exatamente ao termo.
    """
    if not query:
        return None
    alvo = _normalizar(query)
    if not alvo:
        return None

    iso2_para_nome_local = {iso2.lower(): nome for nome, iso2 in MAPA_SIGLAS.items()}

    # 1. Código ISO2 de um país local (ex.: "BR" -> Brasil)
    if alvo in iso2_para_nome_local:
        iso2 = alvo
        return {"id": iso2.upper(), "nome": iso2_para_nome_local[iso2], "iso2": iso2, "fonte": "local"}

    # 2. Nome local (português), com ou sem acento/caixa (ex.: "brasil", "BRASIL" -> Brasil)
    for nome, iso2 in MAPA_SIGLAS.items():
        if alvo == _normalizar(nome):
            return {"id": iso2.upper(), "nome": nome, "iso2": iso2, "fonte": "local"}

    # 3. Universo global (World Bank): nome em inglês ou código ISO2 de qualquer país do mundo.
    #    Se o país resolvido tiver um equivalente monitorado localmente (ex.: "Brazil" -> Brasil,
    #    mesmo iso2 "br"), devolvemos a identidade local — assim buscar em inglês ("Brazil",
    #    "Germany", "United States"...) encontra o mesmo perfil rico que buscar em português.
    try:
        from geopolitica.services.api_service import get_todos_paises_wb, get_iso2_global
        for nome_global in get_todos_paises_wb():
            iso2_global = get_iso2_global(nome_global)
            if alvo == _normalizar(nome_global) or (iso2_global and alvo == iso2_global.lower()):
                if iso2_global and iso2_global.lower() in iso2_para_nome_local:
                    nome_local = iso2_para_nome_local[iso2_global.lower()]
                    return {"id": iso2_global.upper(), "nome": nome_local, "iso2": iso2_global, "fonte": "local"}
                return {
                    "id": (iso2_global or nome_global[:2]).upper(),
                    "nome": nome_global,
                    "iso2": iso2_global,
                    "fonte": "global",
                }
    except Exception:
        pass

    return None
