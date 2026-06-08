import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "paises.csv"

def carregar_dados():
    df = pd.read_csv(CSV_PATH)
    return df


# Ranking por indicador escolhido
def ranking_por_indicador(df, indicador):
    ranking = df.sort_values(by=indicador, ascending=False)

    print(f"\n=== RANKING POR {indicador.upper()} ===")
    print(ranking[["nome", "regiao", indicador]])


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

class Relatorio:
    def __init__(self, df):
        self.df = df

    def exportar_excel(self):
        pasta = Path(__file__).resolve().parent.parent / "media" / "relatorios"
        pasta.mkdir(exist_ok=True)
        caminho = pasta / "relatorio_geopolitico.xlsx"
        self.df.to_excel(caminho, index=False)
        print(f"\nSUCESSO!!!\n Arquivo salvo em: {caminho}")

    def gerar_pdf(self):
        from fpdf import FPDF

        pasta = Path(__file__).resolve().parent.parent / "media" / "relatorios"
        pasta.mkdir(exist_ok=True)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Relatorio Geopolitico - AGPy", ln=True, align="C")
        pdf.ln(5)
            
        pdf.set_font("Arial", "B", 10)
        colunas = ["Nome", "Regiao", "PIB", "Inflacao", "IDH"]
        larguras = [35, 45, 30, 30, 20]
        for i, col in enumerate(colunas):
            pdf.cell(larguras[i], 8, col, border=1)
        pdf.ln()
            
        pdf.set_font("Arial", size=9)
        for _, linha in self.df.iterrows():
            pdf.cell(35, 7, str(linha["nome"]), border=1)
            pdf.cell(45, 7, str(linha["regiao"]), border=1)
            pdf.cell(30, 7, str(linha["pib"]), border=1)
            pdf.cell(30, 7, str(linha["inflacao"]), border=1)
            pdf.cell(20, 7, str(linha["idh"]), border=1)
            pdf.ln()
            
        caminho = pasta / "relatorio_geopolitico.pdf"
        pdf.output(str(caminho))
        print(f"\nSUCESSO! PDF salvo em: {caminho}")


# Menu
def main():
    df = carregar_dados()

    while True:
        print("\n===== MENU =====")
        print("1 - Ver ranking por PIB")
        print("2 - Comparar países")
        print("3 - Filtrar por região")
        print("4 - Exportar dados para Excel")
        print("5 - Exportar dados para PDF")
        print("0 - Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            print("\nOrdenar por qual indicador?")
            print("  a - PIB")
            print("  b - IDH")
            print("  c - Inflacao")
            print("  d - Estabilidade")
            sub = input("Escolha: ")

            mapa = {"a": "pib", "b": "idh", "c": "inflacao", "d": "estabilidade"}
            indicador = mapa.get(sub)

            if indicador:
                ranking_por_indicador(df, indicador)
            else:
                print("Opcao invalida.")

        elif opcao == "2":
            pais1 = input("Digite o primeiro país: ")
            pais2 = input("Digite o segundo país: ")
            comparar_paises(df, pais1, pais2)

        elif opcao == "3":
            regiao = input("Digite a região: ")
            filtrar_por_regiao(df, regiao)

        elif opcao == "4":
            gerador = Relatorio(df)
            gerador.exportar_excel()

        elif opcao == "5":
            gerador = Relatorio(df)
            gerador.gerar_pdf()

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()

