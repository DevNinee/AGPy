# Sistema de Analise Geopolitica (AGPy)

O AGPy e um sistema desenvolvido em Python e estruturado no framework Django para coleta, integracao, analise e visualizacao de dados geopoliticos. A aplicacao permite a comparacao entre paises com base em indicadores economicos e politicos fundamentais, como PIB, Inflacao, e IDH.

## Como o Projeto Foi Desenvolvido

O projeto segue um modelo de expansao em 4 fases e adota a arquitetura MVC (Model-View-Controller) suportada pelo MVT (Model-View-Template) do Django:

- Fase 1 (MVP com Dados Locais): Scripts em Python focados em importar e cruzar dados de arquivos estaticos (CSV) utilizando a biblioteca Pandas. Os modulos de processamento bruto estao preservados na pasta `legacy_scripts/` e integrados em `geopolitica/services/`.
- Fase 2 (Visualizacao Basica): Geracao de graficos comparativos estatisticos com Matplotlib e mapas baseados em HTML usando Folium. As midias geradas dinamicamente sao armazenadas na pasta `media/`.
- Fase 3 (Interface Web): Transicao do terminal para ambiente web com rotas dinâmicas utilizando o framework Django.
- Fase 4 (Consumo Dinamico): Camada de servicos capaz de conectar-se futuramente a APIs externas de instituicoes globais atraves de modulos como `APIHandler` no backend.

O motor analitico inclui pontuacoes ponderadas e uso da biblioteca Scikit-Learn (Inteligencia Artificial) para detectar variacoes percentuais e prever possiveis cenarios de estabilidade politica.

## Estrutura de Diretorios

```
AGPy/
├── agpy/                  # Configuracoes principais do projeto Django (Settings, URLs)
├── data/                  # Fontes de dados locais em formato CSV/JSON
├── docs/                  # Documentacao de requisitos e modelagem estrutural
├── geopolitica/           # Aplicativo central do Django contendo o Controller (views) e Views (templates)
│   ├── services/          # Model: Logicas de inteligencia de dados e integracao (Scikit-Learn, Pandas)
│   ├── templates/         # Arquivos de renderizacao HTML
│   └── static/            # Arquivos estaticos CSS e JS
├── legacy_scripts/        # Codigos iniciais e scripts de execucao pelo terminal para consulta rapida
├── media/                 # Saida dinamica do sistema
│   ├── graficos/          # Exportacoes Matplotlib/Plotly
│   ├── mapas/             # Renderizacoes Folium
│   └── relatorios/        # Saidas do sistema em formato Excel e PDF
└── sandbox_html/          # Arquivos e paginas de testes isolados
```

## Como Instalar e Testar

Siga os passos abaixo para preparar o ambiente virtual e rodar o servidor em sua maquina local.

### 1. Criacao e Ativacao do Ambiente Virtual

Abra o terminal na raiz do projeto e crie um ambiente virtual:

```bash
python3 -m venv venv
```

Ative o ambiente virtual:
- macOS/Linux: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

### 2. Instalacao de Dependencias

Instale as bibliotecas exigidas para processamento de dados e operacao do Django:

```bash
pip install -r requirements.txt
```

### 3. Configuracoes do Banco de Dados

O projeto utiliza o SQLite configurado por padrao, facilitando a portabilidade e testes iniciais. Para inicializar e preparar a base:

```bash
python manage.py migrate
```

### 4. Execucao do Servidor

Para iniciar o servidor local:

```bash
python manage.py runserver
```

Acesse a aplicacao em seu navegador no seguinte endereco local: `http://127.0.0.1:8000/`.

### 5. Execucao de Modulos Auxiliares via Terminal (Opcional)

Se desejar testar a funcionalidade isolada dos scripts originais e modulos da Fase 1, e possivel acionar os codigos contidos no diretorio `legacy_scripts`. Exemplo:

```bash
python legacy_scripts/analise.py
```
