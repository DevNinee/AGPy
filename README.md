# Sistema de Análise Geopolítica (AGPy)

O AGPy é um sistema desenvolvido em Python e estruturado no framework Django para coleta, integração, análise e visualização de dados geopolíticos. A aplicação permite a comparação entre países com base em indicadores econômicos e políticos fundamentais, como PIB, Inflação, e IDH.

## Como o Projeto Foi Desenvolvido

O projeto segue um modelo de expansão em 4 fases e adota a arquitetura MVC (Model-View-Controller) suportada pelo MVT (Model-View-Template) do Django:

- Fase 1 (MVP com Dados Locais): Scripts em Python focados em importar e cruzar dados de arquivos estáticos (CSV) utilizando a biblioteca Pandas. Os módulos de processamento bruto estão preservados na pasta `legacy_scripts/` e integrados em `geopolitica/services/`.
- Fase 2 (Visualização Básica): Geração de gráficos comparativos estatísticos com Matplotlib e mapas baseados em HTML usando Folium. As mídias geradas dinamicamente são armazenadas na pasta `media/`.
- Fase 3 (Interface Web): Transição do terminal para ambiente web com rotas dinâmicas utilizando o framework Django.
- Fase 4 (Consumo Dinâmico): Camada de serviços capaz de conectar-se futuramente a APIs externas de instituições globais através de módulos como `APIHandler` no backend.

O motor analítico inclui pontuações ponderadas e uso da biblioteca Scikit-Learn (Inteligência Artificial) para detectar variações percentuais e prever possíveis cenários de estabilidade política.

## Estrutura de Diretórios

```
AGPy/
├── agpy/                  # Configurações principais do projeto Django (Settings, URLs)
├── data/                  # Fontes de dados locais em formato CSV/JSON
├── docs/                  # Documentação de requisitos e modelagem estrutural
├── geopolitica/           # Aplicativo central do Django contendo o Controller (views) e Views (templates)
│   ├── services/          # Model: Lógicas de inteligência de dados e integração (Scikit-Learn, Pandas)
│   ├── templates/         # Arquivos de renderização HTML
│   └── static/            # Arquivos estáticos CSS e JS
├── legacy_scripts/        # Códigos iniciais e scripts de execução pelo terminal para consulta rápida
├── media/                 # Saída dinâmica do sistema
│   ├── graficos/          # Exportações Matplotlib/Plotly
│   ├── mapas/             # Renderizações Folium
│   └── relatorios/        # Saídas do sistema em formato Excel e PDF
└── sandbox_html/          # Arquivos e páginas de testes isolados
```

## Como Instalar e Testar

Siga os passos abaixo para preparar o ambiente virtual e rodar o servidor em sua máquina local.

### 1. Criação e Ativação do Ambiente Virtual

Abra o terminal na raiz do projeto e crie um ambiente virtual:

```bash
python3 -m venv venv
```

Ative o ambiente virtual:
- macOS/Linux: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

### 2. Instalação de Dependências

Instale as bibliotecas exigidas para processamento de dados e operação do Django:

```bash
pip install -r requirements.txt
```

### 3. Configurações do Banco de Dados

O projeto utiliza o SQLite configurado por padrão, facilitando a portabilidade e testes iniciais. Para inicializar e preparar a base:

```bash
python manage.py migrate
```

### 4. Execução do Servidor

Para iniciar o servidor local:

```bash
python manage.py runserver
```

Acesse a aplicação em seu navegador no seguinte endereço local: `http://127.0.0.1:8000/`.

### 5. Execução de Módulos Auxiliares via Terminal (Opcional)

Se desejar testar a funcionalidade isolada dos scripts originais e módulos da Fase 1, é possível acionar os códigos contidos no diretório `legacy_scripts`. Exemplo:

```bash
python legacy_scripts/analise.py
```
