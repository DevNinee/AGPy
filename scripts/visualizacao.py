import pandas as pd
import matplotlib.pyplot as plt
import folium
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "dados" / "paises.csv"
GRAFICOS_DIR = BASE_DIR / "graficos"
MAPAS_DIR = BASE_DIR / "mapas"

GRAFICOS_DIR.mkdir(exist_ok=True)
MAPAS_DIR.mkdir(exist_ok=True)


def carregar_dados():
    print("Lendo arquivo:", CSV_PATH)
    return pd.read_csv(CSV_PATH)


def grafico_pib():
    df = carregar_dados()
    df = df.sort_values(by="pib", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.bar(df["nome"], df["pib"])
    plt.title("Ranking de PIB por País")
    plt.xlabel("País")
    plt.ylabel("PIB")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / "grafico_pib.png")
    plt.close()


def grafico_idh():
    df = carregar_dados()
    df = df.sort_values(by="idh", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.bar(df["nome"], df["idh"])
    plt.title("Ranking de IDH por País")
    plt.xlabel("País")
    plt.ylabel("IDH")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / "grafico_idh.png")
    plt.close()


def grafico_inflacao():
    df = carregar_dados()
    df = df.sort_values(by="inflacao", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.bar(df["nome"], df["inflacao"])
    plt.title("Inflação por País")
    plt.xlabel("País")
    plt.ylabel("Inflação (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / "grafico_inflacao.png")
    plt.close()


def grafico_estabilidade():
    df = carregar_dados()
    df = df.sort_values(by="estabilidade", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.bar(df["nome"], df["estabilidade"])
    plt.title("Estabilidade Política por País")
    plt.xlabel("País")
    plt.ylabel("Estabilidade")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / "grafico_estabilidade.png")
    plt.close()


def mapa_paises():
    coordenadas = {
        "Brasil": [-14.2350, -51.9253],
        "Estados Unidos": [37.0902, -95.7129],
        "China": [35.8617, 104.1954],
        "Alemanha": [51.1657, 10.4515],
        "Índia": [20.5937, 78.9629],
        "Japão": [36.2048, 138.2529],
        "Canadá": [56.1304, -106.3468],
        "França": [46.2276, 2.2137],
        "Reino Unido": [55.3781, -3.4360],
        "Austrália": [-25.2744, 133.7751]
    }

    df = carregar_dados()
    pib_max = df["pib"].max()
    pib_min = df["pib"].min()
    idh_max = df["idh"].max()
    inflacao_max = df["inflacao"].max()

    def cor_por_pib(pib):
        # Gradiente: vermelho (baixo) → laranja → verde (alto)
        ratio = (pib - pib_min) / (pib_max - pib_min) if pib_max != pib_min else 0.5
        if ratio > 0.66: return "#3fb950"   # verde
        elif ratio > 0.33: return "#f0883e" # laranja
        else: return "#f85149"              # vermelho

    def cor_por_idh(idh):
        if idh >= 0.90: return "#388bfd"
        elif idh >= 0.75: return "#a371f7"
        else: return "#8b949e"

    def cor_por_inflacao(inflacao):
        if inflacao <= 2.5: return "#3fb950"
        elif inflacao <= 5.0: return "#f0883e"
        else: return "#f85149"

    def popup_html(pais):
        cor = cor_por_pib(pais["pib"])
        return f"""
        <div style="
            font-family: Inter, Arial, sans-serif;
            background: #1c2128;
            border: 1px solid #30363d;
            border-top: 3px solid {cor};
            border-radius: 10px;
            padding: 16px;
            width: 240px;
            color: #e6edf3;
        ">
            <h3 style="margin:0 0 12px 0; font-size:15px; color:{cor};">{pais['nome']}</h3>
            <table style="width:100%; border-collapse:collapse; font-size:12px;">
                <tr><td style="color:#8b949e; padding:3px 0;">Região</td><td style="text-align:right;">{pais['regiao']}</td></tr>
                <tr><td style="color:#8b949e; padding:3px 0;">PIB</td><td style="text-align:right;">US$ {pais['pib']} bi</td></tr>
                <tr><td style="color:#8b949e; padding:3px 0;">Inflação</td><td style="text-align:right;">{pais['inflacao']}%</td></tr>
                <tr><td style="color:#8b949e; padding:3px 0;">IDH</td><td style="text-align:right;">{pais['idh']}</td></tr>
                <tr><td style="color:#8b949e; padding:3px 0;">Estabilidade</td><td style="text-align:right;">{pais['estabilidade']}</td></tr>
                <tr><td style="color:#8b949e; padding:3px 0;">Relações</td><td style="text-align:right; font-size:11px;">{pais['relacoes_internacionais']}</td></tr>
            </table>
        </div>
        """

    # Mapa base — OpenStreetMap (funciona sempre, sem chave)
    mapa = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="OpenStreetMap"
    )

    # Camada 1: Por PIB (padrão)
    camada_pib = folium.FeatureGroup(name="Por PIB", show=True)
    # Camada 2: Por IDH
    camada_idh = folium.FeatureGroup(name="Por IDH", show=False)
    # Camada 3: Por Inflação
    camada_inflacao = folium.FeatureGroup(name="Por Inflação", show=False)

    for _, pais in df.iterrows():
        nome = pais["nome"]
        if nome not in coordenadas:
            continue

        loc = coordenadas[nome]
        popup = folium.Popup(folium.IFrame(popup_html(pais), width=260, height=230), max_width=260)

        # Marcadores camada PIB
        folium.CircleMarker(
            location=loc,
            radius=12,
            color=cor_por_pib(pais["pib"]),
            fill=True,
            fill_color=cor_por_pib(pais["pib"]),
            fill_opacity=0.85,
            tooltip=f"{nome} — PIB: US$ {pais['pib']} bi",
            popup=popup
        ).add_to(camada_pib)

        # Marcadores camada IDH
        folium.CircleMarker(
            location=loc,
            radius=12,
            color=cor_por_idh(pais["idh"]),
            fill=True,
            fill_color=cor_por_idh(pais["idh"]),
            fill_opacity=0.85,
            tooltip=f"{nome} — IDH: {pais['idh']}",
            popup=popup
        ).add_to(camada_idh)

        # Marcadores camada Inflação
        folium.CircleMarker(
            location=loc,
            radius=12,
            color=cor_por_inflacao(pais["inflacao"]),
            fill=True,
            fill_color=cor_por_inflacao(pais["inflacao"]),
            fill_opacity=0.85,
            tooltip=f"{nome} — Inflação: {pais['inflacao']}%",
            popup=popup
        ).add_to(camada_inflacao)

    camada_pib.add_to(mapa)
    camada_idh.add_to(mapa)
    camada_inflacao.add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)

    # Salva no lugar certo para o Django servir como static
    destino = BASE_DIR / "geopolitica" / "static" / "mapa" / "mapa_paises.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    mapa.save(str(destino))
    print(f"Mapa salvo em: {destino}")


def gerar_tudo():
    grafico_pib()
    grafico_idh()
    grafico_inflacao()
    grafico_estabilidade()
    mapa_paises()
    print("Gráficos e mapa criados com sucesso!")


if __name__ == "__main__":
    gerar_tudo()