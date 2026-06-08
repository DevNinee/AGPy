"""
Análises baseadas em scikit-learn:
- detecção de tendência de uma série (regressão linear)
- previsão do próximo ano
- classificação geopolítica automática por pontuação
"""
import numpy as np
from sklearn.linear_model import LinearRegression


def detectar_tendencia(anos, valores):
    """
    Analisa a tendência de uma série temporal usando regressão linear.
    
    Retorna: (tipo_tendencia, coeficiente)
        - tipo: 'crescente', 'decrescente' ou 'estável'
        - coeficiente: inclinação da reta de regressão
    """
    if len(anos) < 2 or len(valores) < 2:
        return 'indeterminada', 0.0

    X = np.array(anos, dtype=float).reshape(-1, 1)
    y = np.array(valores, dtype=float)

    modelo = LinearRegression()
    modelo.fit(X, y)
    
    coef = modelo.coef_[0]

    # Mede a inclinação em relação à média, para comparar países de escalas diferentes
    media = np.mean(y)
    if media != 0:
        variacao_relativa = abs(coef / media) * 100
    else:
        variacao_relativa = abs(coef)

    # Abaixo de 2% ao ano consideramos a série estável
    if variacao_relativa > 2:
        if coef > 0:
            return 'crescente', coef
        else:
            return 'decrescente', coef
    else:
        return 'estável', coef


def prever_proximo_ano(anos, valores):
    """
    Usa regressão linear para prever o valor do próximo ano.
    
    Retorna: (ano_previsto, valor_previsto)
    """
    if len(anos) < 2 or len(valores) < 2:
        return max(anos) + 1 if anos else 2024, 0.0

    X = np.array(anos, dtype=float).reshape(-1, 1)
    y = np.array(valores, dtype=float)

    modelo = LinearRegression()
    modelo.fit(X, y)
    
    proximo_ano = max(anos) + 1
    valor_previsto = modelo.predict(np.array([[proximo_ano]]))[0]
    
    return proximo_ano, float(valor_previsto)


def calcular_score_r2(anos, valores):
    """
    Calcula o R² (coeficiente de determinação) da regressão.
    Indica quão bem o modelo linear explica os dados.
    Valor entre 0 e 1 — quanto mais próximo de 1, melhor o ajuste.
    """
    if len(anos) < 2:
        return 0.0

    X = np.array(anos, dtype=float).reshape(-1, 1)
    y = np.array(valores, dtype=float)

    modelo = LinearRegression()
    modelo.fit(X, y)
    
    return modelo.score(X, y)


def classificar_pais_automaticamente(indicadores):
    """
    Classifica um país somando pontos de cada indicador (PIB, arsenal nuclear,
    assento no Conselho de Segurança, gastos militares e IDH).

    indicadores: dict com chaves como 'pib', 'gastos_militares', 'nuclear',
                 'conselho_p5', 'democracia', etc.

    Retorna: (classificacao, score, justificativas)
    """
    score = 0
    justificativas = []

    pib = indicadores.get('pib', 0)
    gastos_mil = indicadores.get('gastos_militares', 0)
    nuclear = indicadores.get('nuclear', False)
    conselho_p5 = indicadores.get('conselho_p5', False)
    democracia = indicadores.get('democracia', 5.0)
    idh = indicadores.get('idh', 0.5)

    # PIB é o critério de maior peso
    if pib > 15000:
        score += 30
        justificativas.append(f"PIB acima de US$ 15 trilhões")
    elif pib > 5000:
        score += 20
        justificativas.append(f"PIB acima de US$ 5 trilhões")
    elif pib > 2000:
        score += 10
        justificativas.append(f"PIB acima de US$ 2 trilhões")
    elif pib > 500:
        score += 5
    
    # Capacidade nuclear
    if nuclear:
        score += 15
        justificativas.append("Possui arsenal nuclear")
    
    # Membro P5 do Conselho de Segurança
    if conselho_p5:
        score += 15
        justificativas.append("Membro permanente do Conselho de Segurança (P5)")
    
    # Gastos militares
    if gastos_mil > 3.0:
        score += 10
        justificativas.append(f"Alto investimento militar ({gastos_mil}% PIB)")
    elif gastos_mil > 2.0:
        score += 5
    
    # IDH
    if idh > 0.9:
        score += 5
    
    # Classificação baseada no score
    if score >= 55:
        classificacao = 'Superpotência'
    elif score >= 30:
        classificacao = 'Grande Potência'
    elif score >= 15:
        classificacao = 'Potência Regional'
    elif score >= 10:
        classificacao = 'Potência Média'
    else:
        classificacao = 'Outro'
    
    return classificacao, score, justificativas
