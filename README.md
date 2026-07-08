# AGPy — Sistema de Análise Geopolítica

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-4.x-0C4B33)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

O **AGPy** é uma plataforma desenvolvida em **Python + Django** para transformar dados geopolíticos em análises comparativas claras e acionáveis.  
A solução integra indicadores econômicos e sociais para apoiar estudos, pesquisas e tomada de decisão com base em dados.

---

## Qual problema o AGPy resolve?

A análise geopolítica costuma ser fragmentada: dados em múltiplas fontes, formatos diferentes e baixa padronização para comparação entre países.  
Isso dificulta responder perguntas como:

- Quais países apresentam maior estabilidade relativa?
- Como inflação, PIB e IDH se relacionam em determinado cenário?
- Quais tendências apontam risco ou oportunidade no curto/médio prazo?

O **AGPy** resolve esse problema ao centralizar, padronizar e analisar os dados em um único fluxo.

---

## Diferenciais do projeto

- Integração de dados em pipeline único: coleta, tratamento, análise e visualização.
- Arquitetura evolutiva em fases: permite crescimento contínuo do sistema sem perder base técnica.
- Comparação entre países com critérios ponderados: facilita leitura analítica dos indicadores.
- Base em ciência de dados: uso de **Pandas** e **Scikit-Learn** para apoiar análises e projeções.
- Visualização multimodal: gráficos estatísticos e mapas interativos para interpretação mais rápida.
- Estrutura híbrida (legado + web): scripts históricos preservados e integrados ao backend Django.

---

## Quem o AGPy ajuda?

O AGPy foi pensado para apoiar:

- Estudantes e pesquisadores de geopolítica, economia e relações internacionais;
- Analistas de dados e inteligência estratégica;
- Instituições acadêmicas e projetos educacionais;
- Usuários que precisam comparar países com base em indicadores objetivos.

---

## Por que fizemos este projeto?

Criamos o AGPy para tornar a análise geopolítica mais acessível, transparente e orientada por dados.  
A proposta é reduzir a distância entre dados brutos e entendimento estratégico, oferecendo uma ferramenta prática para exploração de cenários e apoio à tomada de decisão.

---

## Como o projeto foi desenvolvido

O AGPy segue um modelo de evolução em 4 fases:

1. **Fase 1 (MVP com Dados Locais)**  
   Scripts Python para importação e cruzamento de dados estáticos (CSV), com base em Pandas.

2. **Fase 2 (Visualização Básica)**  
   Geração de gráficos e mapas interativos com Matplotlib/Folium.

3. **Fase 3 (Interface Web)**  
   Migração para ambiente web com Django, rotas dinâmicas e interface de navegação.

4. **Fase 4 (Consumo Dinâmico)**  
   Estrutura preparada para integração futura com APIs externas e fontes globais.

---

## Estrutura de diretórios

```text
AGPy/
├── agpy/                  # Configurações principais do projeto Django (settings, urls)
├── data/                  # Fontes de dados locais em CSV/JSON
├── docs/                  # Documentação técnica e estrutural
├── geopolitica/           # App principal do Django (views, templates, services)
│   ├── services/          # Regras analíticas e integrações (Pandas, Scikit-Learn)
│   ├── templates/         # Templates HTML
│   └── static/            # Arquivos CSS/JS
├── legacy_scripts/        # Scripts iniciais de execução em terminal
├── media/                 # Saídas dinâmicas (gráficos, mapas, relatórios)
└── sandbox_html/          # Área de testes isolados
```

---

## Como instalar e executar

### 1) Criar e ativar ambiente virtual

```bash
python3 -m venv venv
```

macOS/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 3) Aplicar migrações

```bash
python manage.py migrate
```

### 4) Iniciar servidor local

```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000/`

### 5) (Opcional) Executar scripts legados

```bash
python legacy_scripts/analise.py
```

---

## Equipe

- **Camile Felix**
- **Fabiana Souza**
- **Erick Ferreira**
- **Fernanda Ferreira**
- **Emanoel Alexandri**

---

## Status do projeto

Projeto em evolução contínua, com foco em:

- ampliação de fontes de dados;
- melhorias no motor analítico;
- expansão dos recursos de visualização e comparação.

---

# AGPy — Geopolitical Analysis System (English Version)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-4.x-0C4B33)
![Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

**AGPy** is a **Python + Django** platform designed to transform geopolitical data into clear and actionable comparative analysis.  
It integrates economic and social indicators to support research, studies, and data-driven decision-making.

---

## What problem does AGPy solve?

Geopolitical analysis is often fragmented: data comes from multiple sources, in different formats, with little standardization for cross-country comparison.  
This makes it difficult to answer questions such as:

- Which countries show greater relative stability?
- How do inflation, GDP, and HDI relate in a given scenario?
- Which trends indicate risk or opportunity in the short/medium term?

**AGPy** solves this by centralizing, standardizing, and analyzing data in a single workflow.

---

## Project differentiators

- Unified data pipeline: collection, processing, analysis, and visualization.
- Evolutionary phased architecture: supports continuous growth while preserving technical consistency.
- Weighted country comparison model: improves analytical readability across indicators.
- Data science foundation: uses **Pandas** and **Scikit-Learn** for analysis and projections.
- Multi-format visualization: statistical charts and interactive maps for faster interpretation.
- Hybrid structure (legacy + web): preserves legacy scripts while integrating them into Django backend services.

---

## Who does AGPy help?

AGPy is designed for:

- Students and researchers in geopolitics, economics, and international relations;
- Data analysts and strategic intelligence professionals;
- Academic institutions and educational projects;
- Users who need objective, indicator-based country comparisons.

---

## Why did we build this project?

We built AGPy to make geopolitical analysis more accessible, transparent, and data-driven.  
Our goal is to reduce the gap between raw data and strategic understanding through a practical tool for scenario exploration and decision support.

---

## Team

- **Camile Felix**
- **Fabiana Souza**
- **Erick Ferreira**
- **Fernanda Ferreira**
- **Emanoel Alexandri**
