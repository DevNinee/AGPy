import requests


# 1. Criamos a "Caixa de Ferramentas" (Classe) exigida no PDF
class APIHandler:
    
    # O método __init__ prepara a caixa e guarda as configurações das APIs
    def __init__(self, api_key_onu=None):
        # Configurações do Banco Mundial (Aberta, sem chave)
        self.url_base_wb = "https://api.worldbank.org/v2"
        
        # Configurações da ONU/PNUD (Exige chave)
        self.url_base_onu = "https://hdrdata.org/api/CompositeIndices"
        self.api_key_onu = api_key_onu

    # 2. Ferramenta principal que decide de onde buscar os dados
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

    # 3. Lógica específica para o Banco Mundial
    def _buscar_dados_banco_mundial(self, pais, indicador):
        # Montamos a URL completa (ex: country/br/indicator/NY.GDP.MKTP.CD)
        url_completa = f"{self.url_base_wb}/country/{pais}/indicator/{indicador}?format=json"
        
        resposta = requests.get(url_completa)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            # A API do Banco Mundial retorna metadados no índice 0 e os dados no índice 1
            if len(dados) > 1 and dados[1]:
                return dados[1]
            return None
        else:
            print(f"Erro do Banco Mundial (Status: {resposta.status_code})")
            return None

    # 4. Lógica específica para a ONU (IDH, etc)
    def _buscar_dados_onu(self, pais, indicador, ano=None):
        if not self.api_key_onu:
            print("Erro: Para buscar dados da ONU, você precisa fornecer a api_key_onu ao instanciar o APIHandler.")
            print("Cadastre-se em hdrdata.org para obter sua chave.")
            return None
            
        # Estrutura básica para a chamada da ONU
        # Exemplo: /query?apikey=SUA_CHAVE&countryOrAggregation=BRA&indicator=hdi
        # Nota: A API da ONU usa códigos ISO3 (ex: BRA), enquanto Banco Mundial aceita ISO2 (ex: br)
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

    # 5. Busca Global em Lote (World Bank Bulk API)
    def buscar_dados_globais(self, indicador, ano=2022):
        """
        Busca os dados de todos os países do mundo de uma vez só.
        Isso é vital para não travar a aplicação renderizando o mapa/ranking mundial.
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

# =======================================================
# Testando se a nossa Caixa de Ferramentas funciona:
# =======================================================
if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg') # Evita erro de interface gráfica no Mac
    import matplotlib.pyplot as plt

    # Pegamos a caixa (Instanciamos a classe sem a chave da ONU por enquanto)
    api = APIHandler()
    
    print("Buscando dados com a nova Classe (Banco Mundial)...")
    
    # Pedimos a INFLAÇÃO pelo Banco Mundial
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
    
        # Desenhando o gráfico de Inflação
        plt.plot(anos, valores, marker='o', color='red')
        plt.title("Evolução Histórica da Inflação do Brasil (10 Anos)")
        plt.xlabel("Ano")
        plt.ylabel("Inflação (%)")
        plt.grid(True)
        
        # Salvando o gráfico
        from pathlib import Path
        pasta_graficos = Path(__file__).resolve().parent.parent / "media" / "graficos"
        pasta_graficos.mkdir(exist_ok=True) # Garante que a pasta existe
        caminho_arquivo = pasta_graficos / "evolucao_inflacao.png"
        
        plt.savefig(caminho_arquivo)
        print(f"Sucesso! Gráfico salvo em: {caminho_arquivo}")
    else:
        print("Não foi possível obter dados para gerar o gráfico.")
        
    print("\nTestando integração com a ONU (vai falhar intencionalmente sem a chave):")
    api.buscar_dados("BRA", "hdi", fonte="onu")
