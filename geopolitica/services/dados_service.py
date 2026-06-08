"""Acesso centralizado aos dados locais (CSV) e às constantes compartilhadas pelas views."""
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
