import requests


class APIHandler:
    """Cliente para as APIs do Banco Mundial e da ONU/PNUD."""

    def __init__(self, api_key_onu=None):
        # Banco Mundial: API aberta, não precisa de chave
        self.url_base_wb = "https://api.worldbank.org/v2"

        # ONU/PNUD: exige uma chave de acesso
        self.url_base_onu = "https://hdrdata.org/api/CompositeIndices"
        self.api_key_onu = api_key_onu

    def buscar_dados(self, pais, indicador, fonte="world_bank", ano=None):
        """
        Busca dados na API especificada.
        Fontes suportadas: "world_bank" ou "onu"
        """
        if fonte == "world_bank":
            return self._buscar_dados_banco_mundial(pais, indicador)
        elif fonte == "onu":
            return self._buscar_dados_onu(pais, indicador, ano)
        else:
            print(f"Erro: Fonte '{fonte}' desconhecida.")
            return None

    def _buscar_dados_banco_mundial(self, pais, indicador):
        # Ex.: .../country/br/indicator/NY.GDP.MKTP.CD
        url_completa = f"{self.url_base_wb}/country/{pais}/indicator/{indicador}?format=json"

        resposta = requests.get(url_completa)

        if resposta.status_code == 200:
            dados = resposta.json()
            # O índice 0 traz metadados e o índice 1 os dados de fato
            if len(dados) > 1 and dados[1]:
                return dados[1]
            return None
        else:
            print(f"Erro do Banco Mundial (Status: {resposta.status_code})")
            return None

    def _buscar_dados_onu(self, pais, indicador, ano=None):
        if not self.api_key_onu:
            print("Erro: Para buscar dados da ONU, você precisa fornecer a api_key_onu ao instanciar o APIHandler.")
            print("Cadastre-se em hdrdata.org para obter sua chave.")
            return None

        # A ONU usa ISO3 (ex.: BRA), diferente do Banco Mundial, que aceita ISO2 (ex.: br)
        pais_iso3 = pais.upper()
        url_completa = f"{self.url_base_onu}/query?apikey={self.api_key_onu}&countryOrAggregation={pais_iso3}&indicator={indicador}"
        
        if ano:
            url_completa += f"&year={ano}"
            
        resposta = requests.get(url_completa)
        
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print(f"Erro da ONU (Status: {resposta.status_code})")
            return None

    def buscar_dados_globais(self, indicador, ano=2022):
        """
        Busca os dados de todos os países de uma vez só.
        Evita uma chamada por país ao montar o mapa ou o ranking mundial.
        """
        url_completa = f"{self.url_base_wb}/country/all/indicator/{indicador}?format=json&date={ano}&per_page=300"
        try:
            resposta = requests.get(url_completa)
            if resposta.status_code == 200:
                dados = resposta.json()
                if len(dados) > 1 and dados[1]:
                    return dados[1]
            return []
        except Exception as e:
            print("Erro ao buscar dados globais:", e)
            return []

# Teste rápido ao rodar o arquivo direto: gera o gráfico de inflação do Brasil
if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')  # backend sem interface gráfica
    import matplotlib.pyplot as plt

    api = APIHandler()

    print("Buscando dados do Banco Mundial...")

    historico_inflacao = api.buscar_dados("br", "FP.CPI.TOTL.ZG", fonte="world_bank")
    
    if historico_inflacao:
        anos = []
        valores = []
        
        for registro in historico_inflacao[:10]:
            if registro['value'] is not None:
                anos.append(registro['date'])
                valores.append(registro['value'])
                
        anos.reverse()
        valores.reverse()

        plt.plot(anos, valores, marker='o', color='red')
        plt.title("Evolução Histórica da Inflação do Brasil (10 Anos)")
        plt.xlabel("Ano")
        plt.ylabel("Inflação (%)")
        plt.grid(True)

        from pathlib import Path
        pasta_graficos = Path(__file__).resolve().parent.parent / "media" / "graficos"
        pasta_graficos.mkdir(exist_ok=True)
        caminho_arquivo = pasta_graficos / "evolucao_inflacao.png"
        
        plt.savefig(caminho_arquivo)
        print(f"Sucesso! Gráfico salvo em: {caminho_arquivo}")
    else:
        print("Não foi possível obter dados para gerar o gráfico.")
        
    print("\nTeste da ONU (falha de propósito, pois não passamos a chave):")
    api.buscar_dados("BRA", "hdi", fonte="onu")
