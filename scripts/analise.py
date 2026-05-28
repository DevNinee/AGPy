import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "dados" / "paises.csv"

# Função para carregar os dados do CSV
def carregar_dados():
    df = pd.read_csv(CSV_PATH)
    return df


# Ranking por PIB
def ranking_pib(df):
    ranking = df.sort_values(by="pib", ascending=False)

    print("\n=== RANKING POR PIB ===")
    print(ranking[["nome", "regiao", "pib"]])


# Comparar dois países
def comparar_paises(df, pais1, pais2):
    p1 = df[df["nome"] == pais1]
    p2 = df[df["nome"] == pais2]

    if p1.empty or p2.empty:
        print("País não encontrado.")
        return

    print(f"\n=== COMPARAÇÃO: {pais1} vs {pais2} ===")
    print(f"{'Indicador':<25} | {pais1:<15} | {pais2}")
    print("-" * 60)

    colunas = ['pib', 'inflacao', 'idh', 'estabilidade', 'relacoes_internacionais']

    for col in colunas:
        v1 = p1.iloc[0][col]
        v2 = p2.iloc[0][col]
        print(f"{col:<25} | {str(v1):<15} | {v2}")


# Filtro por região
def filtrar_por_regiao(df, regiao):
    resultado = df[df["regiao"].str.contains(regiao, case=False)]

    if resultado.empty:
        print("Nenhum país encontrado.")
    else:
        print("\n=== PAÍSES DA REGIÃO ===")
        print(resultado[["nome", "regiao", "pib"]])

# Menu
def main():
    df = carregar_dados()

    while True:
        print("\n===== MENU =====")
        print("1 - Ver ranking por PIB")
        print("2 - Comparar países")
        print("3 - Filtrar por região")
        print("0 - Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            ranking_pib(df)

        elif opcao == "2":
            pais1 = input("Digite o primeiro país: ")
            pais2 = input("Digite o segundo país: ")
            comparar_paises(df, pais1, pais2)

        elif opcao == "3":
            regiao = input("Digite a região: ")
            filtrar_por_regiao(df, regiao)

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()