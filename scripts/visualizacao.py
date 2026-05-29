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
    mapa = folium.Map(location=[20, 0], zoom_start=2)

    for _, pais in df.iterrows():
        nome = pais["nome"]

        if nome in coordenadas:
            popup = f"""
            <b>{nome}</b><br>
            Região: {pais['regiao']}<br>
            PIB: {pais['pib']}<br>
            Inflação: {pais['inflacao']}%<br>
            IDH: {pais['idh']}<br>
            Estabilidade: {pais['estabilidade']}<br>
            Relações internacionais: {pais['relacoes_internacionais']}
            """

            folium.Marker(
                location=coordenadas[nome],
                popup=popup,
                tooltip=nome
            ).add_to(mapa)

    mapa.save(MAPAS_DIR / "mapa_paises.html")


def gerar_tudo():
    grafico_pib()
    grafico_idh()
    grafico_inflacao()
    grafico_estabilidade()
    mapa_paises()
    print("Gráficos e mapa criados com sucesso!")


if __name__ == "__main__":
    gerar_tudo()