"""Views do sistema de análise geopolítica."""
import io
import json
import base64
import tempfile
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd

from geopolitica.services.dados_service import (
    carregar_dados, get_dado_recente, get_sigla_iso2,
    MAPA_SIGLAS, INDICADORES_DISPONIVEIS, CODIGOS_API_WB,
    validar_indicador,
)
from geopolitica.services.api_service import (
    buscar_dados_cached, buscar_dados_globais_cached,
)
from geopolitica.models import Pais, PerfilGeopolitico, BlocoInternacional


# --- Dashboard principal ---
def index(request):
    historico = buscar_dados_cached("br", "FP.CPI.TOTL.ZG", fonte="world_bank")
    
    inflacao_atual = "Dados Indisponíveis"
    ano_atual = "-"
    if historico:
        for registro in historico:
            if registro.get('value') is not None:
                inflacao_atual = round(registro['value'], 2)
                ano_atual = registro['date']
                break

    # Dados dos perfis geopolíticos para o dashboard
    total_paises = Pais.objects.count()
    total_blocos = BlocoInternacional.objects.count()
    nucleares = PerfilGeopolitico.objects.filter(possui_arsenal_nuclear=True).count()

    context = {
        "inflacao_br": inflacao_atual,
        "ano_br": ano_atual,
        "total_paises": total_paises,
        "total_blocos": total_blocos,
        "nucleares": nucleares,
    }
    return render(request, "geopolitica/index.html", context)


# --- Ranking ---
def ranking(request):
    df = carregar_dados()
    fonte = request.GET.get("fonte", "csv")
    indicador = request.GET.get("indicador", "pib")

    labels_indicador = {
        "pib": "PIB (bilhões USD)",
        "inflacao": "Inflação (%)",
        "idh": "IDH",
    }
    indicador_label = labels_indicador.get(indicador, "PIB (bilhões USD)")

    if fonte == "api":
        wb_indicador = CODIGOS_API_WB.get(indicador, "NY.GDP.MKTP.CD")
        dados_globais = buscar_dados_globais_cached(wb_indicador, ano=2022)
        
        mapa_global = []
        for d in dados_globais:
            val = d.get('value')
            nome = d.get('country', {}).get('value', '')
            iso3 = d.get('countryiso3code', '')
            if val is not None and nome and iso3:
                if indicador == "pib":
                    val = round(val / 1e9, 2)
                mapa_global.append({'nome': nome, 'valor': round(val, 2), 'iso3': iso3})
                
        top_all = sorted(mapa_global, key=lambda x: x['valor'], reverse=True)
        
        ranking_list = []
        for p in top_all:
            ranking_list.append({
                "nome": p['nome'],
                "valor_indicador": p['valor'],
                "pib": p['valor'] if indicador == "pib" else "N/A",
                "inflacao": p['valor'] if indicador == "inflacao" else "N/A",
                "idh": "N/A",
                "estabilidade": "N/A",
                "relacoes_internacionais": "N/A",
                "iso2": p['iso3'][:2].lower()
            })
    else:
        ind_ordem = validar_indicador(indicador)
        ranking_list = df.sort_values(by=ind_ordem, ascending=False).to_dict(orient="records")
        # Campo unificado para o template não precisar saber qual indicador foi escolhido
        for p in ranking_list:
            p["valor_indicador"] = p.get(ind_ordem, "N/A")

    return render(request, "geopolitica/ranking.html", {
        "paises": ranking_list,
        "fonte_atual": fonte,
        "indicador_atual": indicador,
        "indicador_label": indicador_label,
    })


# --- Comparação entre países ---
def comparar(request):
    from geopolitica.services.api_service import get_todos_paises_wb, get_iso2_global, buscar_dados_cached
    from geopolitica.services.dados_service import get_dado_recente
    df = carregar_dados()

    # Usa a lista completa de países da API; se ela falhar, cai para os nomes do CSV
    paises_mestre = get_todos_paises_wb()
    if not paises_mestre:
        paises_mestre = sorted(df["nome"].tolist())
        
    context = {"paises": paises_mestre}

    if request.method == "POST":
        pais1 = request.POST.get("pais1")
        pais2 = request.POST.get("pais2")

        if pais1 and pais2:
            def get_dados_pais(nome_pais):
                dados_csv = df[df["nome"] == nome_pais].to_dict(orient="records")
                if dados_csv:
                    return dict(dados_csv[0])
                else:
                    return {
                        "nome": nome_pais,
                        "regiao": "Global",
                        "pib": "N/A",
                        "inflacao": "N/A",
                        "idh": "N/A",
                        "estabilidade": "N/A",
                        "pib_per_capita": "N/A",
                        "gastos_militares": "N/A",
                        "divida_publica": "N/A",
                        "gini": "N/A",
                        "indice_democracia": "N/A",
                        "relacoes_internacionais": "N/A"
                    }

            resultado_p1 = get_dados_pais(pais1)
            resultado_p2 = get_dados_pais(pais2)

            # Completa os dados locais com valores ao vivo da API
            for resultado, nome_pais in [(resultado_p1, pais1), (resultado_p2, pais2)]:
                # Tenta a sigla do CSV; se não houver, busca no mapa global do World Bank
                sigla = get_sigla_iso2(nome_pais)
                if not sigla:
                    sigla = get_iso2_global(nome_pais)
                
                    if sigla:
                        pib_vivo = get_dado_recente(
                            buscar_dados_cached(sigla, "NY.GDP.MKTP.CD", fonte="world_bank"), 1e9
                        )
                        inf_vivo = get_dado_recente(
                            buscar_dados_cached(sigla, "FP.CPI.TOTL.ZG", fonte="world_bank")
                        )
                        pib_pc = get_dado_recente(
                            buscar_dados_cached(sigla, "NY.GDP.PCAP.CD", fonte="world_bank")
                        )
                        gastos_mil = get_dado_recente(
                            buscar_dados_cached(sigla, "MS.MIL.XPND.GD.ZS", fonte="world_bank")
                        )
                        gini = get_dado_recente(
                            buscar_dados_cached(sigla, "SI.POV.GINI", fonte="world_bank")
                        )
                        
                        if pib_vivo:
                            resultado["pib"] = f"{pib_vivo} bi (API)"
                        if inf_vivo:
                            resultado["inflacao"] = f"{inf_vivo}% (API)"
                        if pib_pc:
                            resultado["pib_per_capita"] = f"{pib_pc:,.2f} (API)"
                        if gastos_mil:
                            resultado["gastos_militares"] = f"{gastos_mil} (API)"
                        if gini:
                            resultado["gini"] = f"{gini} (API)"
                        
                        if resultado["idh"] == "N/A":
                            resultado["idh"] = "N/A (Apenas Base Local)"
                            resultado["estabilidade"] = "N/A (Apenas Base Local)"
                            resultado["indice_democracia"] = "N/A (Apenas Base Local)"
                            resultado["relacoes_internacionais"] = "Análise qualitativa restrita aos países do CSV."

            perfil_p1 = _get_perfil_dict(pais1)
            perfil_p2 = _get_perfil_dict(pais2)

            context["resultado"] = {
                "pais1": resultado_p1,
                "pais2": resultado_p2,
                "perfil_p1": perfil_p1,
                "perfil_p2": perfil_p2,
            }

    return render(request, "geopolitica/comparar.html", context)


def _get_perfil_dict(nome_pais):
    """Busca perfil geopolítico do banco e retorna como dict."""
    try:
        pais_obj = Pais.objects.get(nome=nome_pais)
        perfil = pais_obj.perfil
        blocos = list(pais_obj.blocos.values_list('nome', flat=True))
        return {
            "classificacao": perfil.get_classificacao_display(),
            "nuclear": perfil.possui_arsenal_nuclear,
            "conselho": perfil.get_membro_conselho_seguranca_display(),
            "gastos_mil": perfil.gastos_militares_pct_pib,
            "democracia": perfil.indice_democracia,
            "disputas": perfil.disputas_territoriais,
            "observacoes": perfil.observacoes,
            "blocos": blocos,
        }
    except (Pais.DoesNotExist, PerfilGeopolitico.DoesNotExist):
        return None


# --- Mapa interativo ---
def _iso3_para_iso2(iso3):
    """Converte um código ISO3 (ex: 'RUS') no ISO2 minúsculo usado pelo flagcdn (ex: 'ru')."""
    if not iso3:
        return ""
    try:
        import pycountry
        pais = pycountry.countries.get(alpha_3=iso3.upper())
        if pais:
            return pais.alpha_2.lower()
    except Exception:
        pass
    return ""


def mapa(request):
    df = carregar_dados()
    fonte = request.GET.get("fonte", "api")  # mapa abre com dados globais por padrão
    indicador = request.GET.get("indicador", "pib")
    regiao_filtro = request.GET.get("regiao", "")

    paises_json = []
    cores_paises = {}
    paises_regiao = []
    regioes = sorted(df["regiao"].unique().tolist())

    if fonte == "api":
        from geopolitica.services.api_service import get_todos_paises_wb
        paises_validos = set(get_todos_paises_wb())
        
        wb_indicador = CODIGOS_API_WB.get(indicador, "NY.GDP.MKTP.CD")
        dados_globais = buscar_dados_globais_cached(wb_indicador, ano=2022)

        valores_validos = []
        mapa_global = []

        for d in dados_globais:
            val = d.get('value')
            if val is not None:
                iso3 = d.get('countryiso3code')
                nome = d.get('country', {}).get('value', '')
                if iso3 and nome and nome in paises_validos:
                    if indicador == "pib":
                        val = round(val / 1e9, 2)
                    valores_validos.append(val)
                    mapa_global.append({'nome': nome, 'iso3': iso3, 'valor': round(val, 2)})

        if valores_validos:
            v_max = max(valores_validos)
            v_min = min(valores_validos)
            
            for item in mapa_global:
                iso3 = item['iso3']
                valor = item['valor']
                
                paises_json.append({
                    "nome": item['nome'],
                    "pib": valor if indicador == "pib" else "N/A",
                    "inflacao": valor if indicador == "inflacao" else "N/A",
                    "iso3": iso3,
                    "iso2": _iso3_para_iso2(iso3),
                })

                cor = _cor_por_indicador_global(indicador, valor, v_min, v_max)
                cores_paises[item['nome']] = cor
                cores_paises[iso3] = cor

            top_all = sorted(mapa_global, key=lambda x: x['valor'], reverse=True)
            paises_regiao = [{"nome": x['nome'], indicador: x['valor']} for x in top_all]

    else:
        paises_json = df.to_dict(orient="records")
        for p in paises_json:
            p["iso2"] = get_sigla_iso2(p["nome"])
        pib_max = df["pib"].max()
        pib_min = df["pib"].min()

        for _, pais in df.iterrows():
            nome = pais["nome"]
            na_regiao = (not regiao_filtro) or (regiao_filtro.lower() in pais["regiao"].lower())

            if not na_regiao:
                cores_paises[nome] = "#30363d"
                continue

            ind = validar_indicador(indicador)
            valor = pais[ind] if ind in pais else pais["pib"]
            cor = _cor_por_indicador_local(indicador, valor, pib_min, pib_max)
            cores_paises[nome] = cor

        if regiao_filtro:
            df_regiao = df[df["regiao"].str.lower().str.contains(regiao_filtro.lower())]
        else:
            df_regiao = df

        ind_ordem = validar_indicador(indicador)
        paises_regiao = df_regiao.sort_values(by=ind_ordem, ascending=False).to_dict(orient="records")

    context = {
        "paises_json": json.dumps(paises_json),
        "cores_paises": json.dumps(cores_paises),
        "paises_ranking": paises_regiao,
        "indicador_atual": indicador,
        "regiao_atual": regiao_filtro,
        "regioes": regioes,
        "fonte_atual": fonte,
    }
    return render(request, "geopolitica/mapa.html", context)


def _cor_por_indicador_global(indicador, valor, v_min, v_max):
    """Cor para indicadores em modo API global."""
    if indicador == "pib":
        ratio = (valor - v_min) / (v_max - v_min) if v_max != v_min else 0.5
        if ratio > 0.05: return "#3fb950"
        elif ratio > 0.005: return "#f0883e"
        else: return "#f85149"
    elif indicador == "inflacao":
        if valor <= 4.0: return "#3fb950"
        elif valor <= 10.0: return "#f0883e"
        else: return "#f85149"
    return "#30363d"


def _cor_por_indicador_local(indicador, valor, pib_min, pib_max):
    """Cor para indicadores em modo CSV local."""
    if indicador == "pib" or indicador not in ["idh", "inflacao", "indice_democracia"]:
        ratio = (valor - pib_min) / (pib_max - pib_min) if pib_max != pib_min else 0.5
        if ratio > 0.66: return "#3fb950"
        elif ratio > 0.33: return "#f0883e"
        else: return "#f85149"
    elif indicador == "idh":
        if valor >= 0.90: return "#388bfd"
        elif valor >= 0.75: return "#a371f7"
        else: return "#8b949e"
    elif indicador == "inflacao":
        if valor <= 2.5: return "#3fb950"
        elif valor <= 5.0: return "#f0883e"
        else: return "#f85149"
    elif indicador == "indice_democracia":
        if valor >= 8.0: return "#3fb950"
        elif valor >= 6.0: return "#f0883e"
        else: return "#f85149"
    return "#30363d"


# --- Gráficos (renderizados com Matplotlib no servidor) ---
def graficos(request):
    df = carregar_dados()
    fonte = request.GET.get("fonte", "csv")
    indicador = request.GET.get("indicador", "pib")

    labels_map = {
        "pib": ("PIB (bilhões USD)", "PIB"),
        "idh": ("IDH por País", "IDH"),
        "inflacao": ("Inflação (%)", "Inflação (%)"),
        "estabilidade": ("Estabilidade Política", "Estabilidade"),
        "pib_per_capita": ("PIB per Capita (USD PPP)", "PIB per Capita"),
        "gastos_militares": ("Gastos Militares (% PIB)", "% PIB"),
        "divida_publica": ("Dívida Pública (% PIB)", "% PIB"),
        "gini": ("Índice de Gini", "Gini"),
        "indice_democracia": ("Índice de Democracia (EIU)", "Score"),
    }

    if indicador not in labels_map:
        indicador = "pib"

    titulo_base, eixo_y = labels_map[indicador]

    if fonte == "api":
        from geopolitica.services.api_service import get_todos_paises_wb
        paises_validos = set(get_todos_paises_wb())
        
        wb_indicador = CODIGOS_API_WB.get(indicador, "NY.GDP.MKTP.CD")
        dados_globais = buscar_dados_globais_cached(wb_indicador, ano=2022)
        
        mapa_global = []
        for d in dados_globais:
            val = d.get('value')
            nome = d.get('country', {}).get('value', '')
            iso3 = d.get('countryiso3code', '')
            if val is not None and nome and iso3 and nome in paises_validos:
                if indicador == "pib":
                    val = round(val / 1e9, 2)
                mapa_global.append({'nome': nome, 'valor': round(val, 2)})
                
        top_15 = sorted(mapa_global, key=lambda x: x['valor'], reverse=True)[:15]
        
        nomes = [x['nome'] for x in top_15]
        valores = [x['valor'] for x in top_15]
        titulo = f"Top 15 Mundo: {titulo_base}"
    else:
        ind = validar_indicador(indicador)
        if ind not in df.columns:
            ind = "pib"
        df_sorted = df.sort_values(by=ind, ascending=False)
        nomes = df_sorted["nome"].tolist()
        valores = df_sorted[ind].tolist()
        titulo = f"Países Locais: {titulo_base}"

    cores = ["#388bfd", "#a371f7", "#3fb950", "#f0883e", "#f85149"] * 5

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor("#161b22")
    ax.set_facecolor("#1c2128")

    bars = ax.bar(nomes, valores, color=cores[:len(nomes)], width=0.6)

    ax.set_title(titulo, color="#e6edf3", fontsize=14, pad=14)
    ax.set_xlabel("País", color="#8b949e", fontsize=10)
    ax.set_ylabel(eixo_y, color="#8b949e", fontsize=10)
    ax.tick_params(axis="x", rotation=35, colors="#8b949e", labelsize=9)
    ax.tick_params(axis="y", colors="#8b949e", labelsize=9)
    ax.spines["bottom"].set_color("#30363d")
    ax.spines["left"].set_color("#30363d")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color="#21262d", linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    buffer.seek(0)
    imagem_b64 = base64.b64encode(buffer.read()).decode("utf-8")

    context = {
        "imagem": imagem_b64,
        "indicador_atual": indicador,
        "paises": df["nome"].tolist(),
        "indicadores": INDICADORES_DISPONIVEIS,
    }
    return render(request, "geopolitica/graficos.html", context)


# --- Histórico temporal (Chart.js no browser + World Bank API) ---
def historico(request):
    from geopolitica.services.api_service import get_todos_paises_wb
    df = carregar_dados()
    paises_global = get_todos_paises_wb()
    if not paises_global:
        paises_global = sorted(df["nome"].tolist())
    context = {"paises": paises_global}
    return render(request, "geopolitica/historico.html", context)


def historico_dados(request):
    """Endpoint JSON chamado pelo Chart.js no browser."""
    from geopolitica.services.api_service import get_iso2_global
    pais_nome = request.GET.get("pais", "Brasil")
    sigla = get_sigla_iso2(pais_nome)
    if not sigla:
        sigla = get_iso2_global(pais_nome)
    if not sigla:
        sigla = "br"  # fallback final
    indicador = request.GET.get("indicador", "inflacao")

    codigo_wb = CODIGOS_API_WB.get(indicador, "FP.CPI.TOTL.ZG")

    historico = buscar_dados_cached(sigla, codigo_wb, fonte="world_bank")

    anos, valores = [], []
    if historico:
        dados_filtrados = [(r["date"], r["value"]) for r in historico if r.get("value") is not None]
        dados_filtrados = sorted(dados_filtrados[-15:], key=lambda x: x[0])
        for ano, valor in dados_filtrados:
            anos.append(ano)
            if indicador == "pib":
                valores.append(round(valor / 1e9, 2))
            else:
                valores.append(round(valor, 2))

    # Tendência e previsão da série (precisa de pelo menos 3 anos para valer a pena)
    tendencia = None
    previsao = None
    try:
        from geopolitica.services.analise_service import detectar_tendencia, prever_proximo_ano
        if len(anos) >= 3:
            int_anos = [int(a) for a in anos]
            tendencia_tipo, coef = detectar_tendencia(int_anos, valores)
            tendencia = {"tipo": tendencia_tipo, "coeficiente": round(coef, 4)}
            prox_ano, prox_valor = prever_proximo_ano(int_anos, valores)
            previsao = {"ano": prox_ano, "valor": round(prox_valor, 2)}
    except ImportError:
        pass  # sem o service de análise, devolve só os dados brutos

    return JsonResponse({
        "pais": pais_nome,
        "indicador": indicador,
        "codigo_wb": codigo_wb,
        "anos": anos,
        "valores": valores,
        "tendencia": tendencia,
        "previsao": previsao,
    })


# --- Busca de países ---
def buscar(request):
    import requests as http_requests

    df = carregar_dados()
    query = request.GET.get("q", "").strip()
    resultado = None
    nao_encontrado = False
    perfil = None

    if query:
        # Tenta busca local exata
        encontrado = df[df["nome"].str.lower() == query.lower()]
        if not encontrado.empty:
            resultado = encontrado.iloc[0].to_dict()
            resultado['iso2'] = get_sigla_iso2(resultado['nome']) or "br"
            perfil = _get_perfil_dict(resultado['nome'])
        else:
            # Tenta busca parcial local
            parcial = df[df["nome"].str.lower().str.contains(query.lower())]
            if not parcial.empty:
                resultado = parcial.iloc[0].to_dict()
                resultado['iso2'] = get_sigla_iso2(resultado['nome']) or "br"
                perfil = _get_perfil_dict(resultado['nome'])
            else:
                # Fallback: RestCountries API
                try:
                    resp = http_requests.get(f"https://restcountries.com/v3.1/translation/{query}", timeout=5)
                    if resp.status_code == 200:
                        dados_rc = resp.json()[0]
                        cca2 = dados_rc.get("cca2", "").lower()
                        nome_oficial = dados_rc.get("translations", {}).get("por", {}).get("common", dados_rc.get("name", {}).get("common", query))
                        regiao = dados_rc.get("region", "Desconhecida")
                        
                        pib_vivo = get_dado_recente(
                            buscar_dados_cached(cca2, "NY.GDP.MKTP.CD", fonte="world_bank"), 1e9
                        )
                        inf_vivo = get_dado_recente(
                            buscar_dados_cached(cca2, "FP.CPI.TOTL.ZG", fonte="world_bank")
                        )
                        pib_pc = get_dado_recente(
                            buscar_dados_cached(cca2, "NY.GDP.PCAP.CD", fonte="world_bank")
                        )
                        gastos_mil = get_dado_recente(
                            buscar_dados_cached(cca2, "MS.MIL.XPND.GD.ZS", fonte="world_bank")
                        )
                        gini = get_dado_recente(
                            buscar_dados_cached(cca2, "SI.POV.GINI", fonte="world_bank")
                        )
                        
                        resultado = {
                            "nome": nome_oficial,
                            "regiao": regiao,
                            "pib": f"{pib_vivo} (API)" if pib_vivo is not None else "N/A",
                            "inflacao": f"{inf_vivo} (API)" if inf_vivo is not None else "N/A",
                            "pib_per_capita": f"{pib_pc:,.2f} (API)" if pib_pc is not None else "N/A",
                            "gastos_militares": f"{gastos_mil} (API)" if gastos_mil is not None else "N/A",
                            "gini": f"{gini} (API)" if gini is not None else "N/A",
                            "idh": "N/A (Apenas Base Local)",
                            "estabilidade": "N/A (Apenas Base Local)",
                            "relacoes_internacionais": "As análises qualitativas sobre Relações Internacionais e Política Externa estão disponíveis exclusivamente para os países monitorados localmente no banco de dados. Este perfil foi gerado dinamicamente via World Bank API e RestCountries API.",
                            "iso2": cca2
                        }
                    else:
                        nao_encontrado = True
                except Exception as e:
                    print("Erro na API:", e)
                    nao_encontrado = True

    context = {
        "resultado": resultado,
        "perfil": perfil,
        "query": query,
        "nao_encontrado": nao_encontrado,
        "paises": df["nome"].tolist(),
    }
    return render(request, "geopolitica/buscar.html", context)


# --- Exportação de relatórios ---
def _get_df_for_export(request):
    fonte = request.GET.get("fonte", "csv")
    indicador = request.GET.get("indicador", "pib")
    df = carregar_dados()

    if fonte == "api":
        from geopolitica.services.api_service import get_todos_paises_wb
        paises_validos = set(get_todos_paises_wb())
        
        wb_indicador = CODIGOS_API_WB.get(indicador, "NY.GDP.MKTP.CD")
        dados_globais = buscar_dados_globais_cached(wb_indicador, ano=2022)
        
        mapa_global = []
        for d in dados_globais:
            val = d.get('value')
            nome = d.get('country', {}).get('value', '')
            iso3 = d.get('countryiso3code', '')
            if val is not None and nome and iso3 and nome in paises_validos:
                if indicador == "pib":
                    val = round(val / 1e9, 2)
                mapa_global.append({'nome': nome, 'valor': val})
                
        top_all = sorted(mapa_global, key=lambda x: x['valor'], reverse=True)
        
        ranking_list = []
        for p in top_all:
            ranking_list.append({
                "nome": p['nome'],
                "regiao": "Global",
                "pib": p['valor'] if indicador == "pib" else "N/A",
                "inflacao": p['valor'] if indicador == "inflacao" else "N/A",
                "idh": p['valor'] if indicador == "idh" else "N/A"
            })
        return pd.DataFrame(ranking_list)
    else:
        ind_ordem = validar_indicador(indicador)
        df = df.sort_values(by=ind_ordem, ascending=False)
        return df

def exportar_excel(request):
    df = _get_df_for_export(request)
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Geopolítica')
    
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="relatorio_geopolitico.xlsx"'
    return response


def exportar_pdf(request):
    from fpdf import FPDF

    df = _get_df_for_export(request)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatorio Geopolitico - AGPy", ln=True, align="C")
    pdf.ln(5)
        
    pdf.set_font("Arial", "B", 10)
    colunas = ["Nome", "Regiao", "PIB (Bi)", "Inflacao", "IDH"]
    larguras = [35, 45, 30, 30, 20]
    
    for i, col in enumerate(colunas):
        pdf.cell(larguras[i], 8, col, border=1)
    pdf.ln()
        
    pdf.set_font("Arial", size=9)
    for _, linha in df.iterrows():
        nome = str(linha["nome"])[:20]
        regiao = str(linha["regiao"])[:25]
        pib = str(linha["pib"])
        inflacao = str(linha["inflacao"])
        idh = str(linha["idh"])
        
        pdf.cell(35, 7, nome, border=1)
        pdf.cell(45, 7, regiao, border=1)
        pdf.cell(30, 7, pib, border=1)
        pdf.cell(30, 7, inflacao, border=1)
        pdf.cell(20, 7, idh, border=1)
        pdf.ln()

    fd, path = tempfile.mkstemp(suffix=".pdf")
    try:
        os.close(fd)
        pdf.output(path)
        with open(path, "rb") as f:
            pdf_data = f.read()
    finally:
        os.remove(path)

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_geopolitico.pdf"'
    return response


# --- Classificação geopolítica ---
def classificacao(request):
    """Lista a classificação geopolítica de todos os países monitorados no banco."""
    paises = Pais.objects.prefetch_related('perfil', 'blocos', 'indicadores').all()
    
    paises_data = []
    for pais in paises:
        try:
            perfil = pais.perfil
        except PerfilGeopolitico.DoesNotExist:
            perfil = None
        
        blocos = list(pais.blocos.values_list('nome', flat=True))

        indicadores = {}
        for ind in pais.indicadores.filter(ano=2023):
            indicadores[ind.tipo] = ind.valor
        
        paises_data.append({
            "nome": pais.nome,
            "regiao": pais.regiao,
            "iso2": pais.codigo_iso2,
            "classificacao": perfil.get_classificacao_display() if perfil else "N/A",
            "classificacao_cod": perfil.classificacao if perfil else "",
            "nuclear": perfil.possui_arsenal_nuclear if perfil else False,
            "conselho": perfil.get_membro_conselho_seguranca_display() if perfil else "N/A",
            "gastos_mil": perfil.gastos_militares_pct_pib if perfil else None,
            "democracia": perfil.indice_democracia if perfil else None,
            "disputas": perfil.disputas_territoriais if perfil else "",
            "observacoes": perfil.observacoes if perfil else "",
            "blocos": blocos,
            "pib": indicadores.get("pib"),
            "idh": indicadores.get("idh"),
        })
    
    blocos_list = BlocoInternacional.objects.prefetch_related('paises').all()
    blocos_data = []
    for bloco in blocos_list:
        blocos_data.append({
            "nome": bloco.nome,
            "tipo": bloco.get_tipo_display(),
            "descricao": bloco.descricao,
            "membros": list(bloco.paises.values_list('nome', flat=True)),
        })

    context = {
        "paises": paises_data,
        "blocos": blocos_data,
    }
    return render(request, "geopolitica/classificacao.html", context)