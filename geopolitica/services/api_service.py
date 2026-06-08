"""
Wrapper do APIHandler com cache em memória.
Evita chamadas repetidas à API durante a mesma execução do servidor.
"""
import time
from legacy_scripts.api_handler import APIHandler

# Cache simples em memória — suficiente para MVP
# Em produção, substituir por Redis ou Django Cache Framework
_cache = {}
_CACHE_TTL = 3600  # 1 hora em segundos


def _cache_key(pais, indicador, fonte, ano=None):
    return f"{fonte}:{pais}:{indicador}:{ano}"


def buscar_dados_cached(pais, indicador, fonte="world_bank", ano=None):
    """
    Busca dados com cache — evita chamadas repetidas à API.
    Cada resultado fica em cache por 1 hora.
    """
    key = _cache_key(pais, indicador, fonte, ano)
    
    # Verifica cache
    if key in _cache:
        dados, timestamp = _cache[key]
        if time.time() - timestamp < _CACHE_TTL:
            return dados
    
    # Cache miss — busca na API
    api = APIHandler()
    resultado = api.buscar_dados(pais, indicador, fonte=fonte, ano=ano)
    
    # Armazena no cache
    _cache[key] = (resultado, time.time())
    return resultado


def buscar_dados_globais_cached(indicador_wb, ano=2022):
    """
    Busca dados globais com cache.
    """
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
                paises = [p for p in res[1] if p.get('region', {}).get('value') != 'Aggregates']
                
                # Armazenar mapeamento global nome -> iso2
                mapa_global = {p['name']: p['iso2Code'].lower() for p in paises if p.get('iso2Code')}
                _cache["mapa_global_iso2"] = (mapa_global, __import__('time').time())
                
                paises_nomes = sorted([p['name'] for p in paises])
                _cache[cache_key] = (paises_nomes, __import__('time').time())
                return paises_nomes
    except Exception as e:
        print("Erro get_todos_paises_wb:", e)
    
    return []

def get_iso2_global(nome_pais):
    get_todos_paises_wb() # Garante que o cache está populado
    if "mapa_global_iso2" in _cache:
        mapa, _ = _cache["mapa_global_iso2"]
        return mapa.get(nome_pais, "")
    return ""
