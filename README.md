# AGPy - Sistema de Análise Geopolítica

Trabalho acadêmico de Novas Tecnologias: Sistema de análise geopolítica desenvolvido em Python.
Este projeto atende a **todas as Fases (1 a 4)** exigidas, englobando desde a manipulação local de CSVs via Pandas no terminal até uma interface Web completa (Django) que consome dados em tempo real da API do Banco Mundial.

## Passo a Passo: Como Rodar o Projeto

### 1. Preparando o Ambiente
Antes de rodar o sistema, ative seu ambiente virtual e instale as dependências:

```bash
# Ative o ambiente virtual (se estiver na pasta raiz onde o .venv foi criado)
source .venv/bin/activate

# Entre na pasta do sistema
cd AGPy

# Instale as dependências
pip install -r requirements.txt
```

### 2. A Aplicação Web Principal (Dashboard Completo - Fases 2, 3 e 4)
A interface gráfica completa com mapas dinâmicos, gráficos interativos gerados sob demanda e consumo de API em tempo real roda no navegador via Django.

**Comando para subir o servidor:**
```bash
python manage.py runserver
```
*Após rodar o comando, abra o seu navegador e acesse: [http://127.0.0.1:8000](http://127.0.0.1:8000)*

Na interface web você encontrará:
- **Painel Principal:** Dados da inflação brasileira em tempo real (API).
- **Ranking:** Tabelas dinâmicas de países.
- **Comparação:** Compare dois países lado a lado com dados locais (CSV) + dados ao vivo (API).
- **Gráficos:** Gráficos gerados com Matplotlib e embutidos diretamente no HTML.
- **Histórico:** Gráfico interativo (Chart.js) consumindo histórico de inflação/PIB dos últimos 15 anos via World Bank API.
- **Mapa:** Mapa Coroplético interativo usando Leaflet.

### 3. A Aplicação de Terminal (Fase 1)
Se o avaliador quiser testar a lógica pura do terminal (MVP Inicial), nós mantivemos o script original com o menu interativo.

**Comando para executar o menu no terminal:**
```bash
python scripts/analise.py
```
*Através deste script você pode gerar relatórios em Excel (.xlsx) e PDF nativamente na pasta `relatorios/`.*
