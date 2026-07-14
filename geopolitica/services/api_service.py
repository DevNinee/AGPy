"""
Wrapper do APIHandler com cache em memória.
Evita chamadas repetidas à API durante a mesma execução do servidor.
"""
import time
from legacy_scripts.api_handler import APIHandler

# Cache em memória do processo. Para produção valeria trocar por Redis ou o cache do Django.
_cache = {}
_CACHE_TTL = 3600  # segundos


def _cache_key(pais, indicador, fonte, ano=None):
    return f"{fonte}:{pais}:{indicador}:{ano}"


def buscar_dados_cached(pais, indicador, fonte="world_bank", ano=None):
    """Busca os dados de um país, reaproveitando o cache por até uma hora."""
    key = _cache_key(pais, indicador, fonte, ano)

    if key in _cache:
        dados, timestamp = _cache[key]
        if time.time() - timestamp < _CACHE_TTL:
            return dados

    api = APIHandler()
    resultado = api.buscar_dados(pais, indicador, fonte=fonte, ano=ano)
    _cache[key] = (resultado, time.time())
    return resultado


def buscar_dados_globais_cached(indicador_wb, ano=2022):
    """Busca os dados de todos os países de uma vez, com cache."""
    key = f"global:{indicador_wb}:{ano}"
    
    if key in _cache:
        dados, timestamp = _cache[key]
        if time.time() - timestamp < _CACHE_TTL:
            return dados
    
    api = APIHandler()
    resultado = api.buscar_dados_globais(indicador_wb, ano=ano)
    
    _cache[key] = (resultado, time.time())
    return resultado


def limpar_cache():
    """Limpa o cache manualmente se necessário."""
    _cache.clear()

def get_todos_paises_wb():
    cache_key = "lista_todos_paises_wb"
    if cache_key in _cache:
        dados, timestamp = _cache[cache_key]
        return dados
    
    import requests
    url = "http://api.worldbank.org/v2/country?format=json&per_page=300"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            res = r.json()
            if len(res) > 1 and res[1]:
                # Remove os "Aggregates" (regiões e grupos de renda), deixando só países
                paises = [p for p in res[1] if p.get('region', {}).get('value') != 'Aggregates']

                # Guarda também o mapa nome -> iso2 para resolver siglas depois
                mapa_global = {p['name']: p['iso2Code'].lower() for p in paises if p.get('iso2Code')}
                _cache["mapa_global_iso2"] = (mapa_global, __import__('time').time())

                # E o mapa nome -> região (usado para filtrar o mapa por região no modo API)
                mapa_regiao = {p['name']: p.get('region', {}).get('value', '').strip() for p in paises}
                _cache["mapa_global_regiao"] = (mapa_regiao, __import__('time').time())

                paises_nomes = sorted([p['name'] for p in paises])
                _cache[cache_key] = (paises_nomes, __import__('time').time())
                return paises_nomes
    except Exception as e:
        print("Erro get_todos_paises_wb:", e)

    return []

def get_iso2_global(nome_pais):
    get_todos_paises_wb()  # garante que o mapa de siglas já foi carregado
    if "mapa_global_iso2" in _cache:
        mapa, _ = _cache["mapa_global_iso2"]
        return mapa.get(nome_pais, "")
    return ""


def get_regiao_global(nome_pais):
    """Região (World Bank) de um país do universo global. Ex.: 'Latin America & Caribbean'."""
    get_todos_paises_wb()
    if "mapa_global_regiao" in _cache:
        mapa, _ = _cache["mapa_global_regiao"]
        return mapa.get(nome_pais, "")
    return ""


def get_regioes_wb():
    """Lista de regiões distintas do universo global, para popular o filtro do mapa no modo API."""
    get_todos_paises_wb()
    if "mapa_global_regiao" in _cache:
        mapa, _ = _cache["mapa_global_regiao"]
        return sorted({regiao for regiao in mapa.values() if regiao})
    return []
