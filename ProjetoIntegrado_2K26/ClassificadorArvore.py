# ============================================================
# CLASSIFICADOR DE QUALIDADE DO AR
# ============================================================
#
# Este programa recebe um valor ADC enviado pelo Node.js,
# converte esse valor para uma concentração simulada de CO2
# e utiliza uma Árvore de Decisão para classificar a qualidade
# do ar.
#
# O sensor utilizado como REFERÊNCIA para a simulação é o
# MH-Z19B, um sensor de CO2
#
# Faixa utilizada nesta simulação:
#
#       0 ppm  -> 5000 ppm
#       0 adc  -> 4095 adc
#
# Portanto fazemos uma regra de três:
# Fórmula:
#
#       CO2 = (ADC * 5000) / 4095

# ============================================================
# BIBLIOTECAS
# ============================================================

# Importa a Árvore de Decisão do Scikit-learn.
# Ela será utilizada para aprender a relação entre: CO2 -> qualidade do ar
from sklearn.tree import DecisionTreeClassifier

# Será utilizado para receber o ADC enviado pelo Node.js.
# sys.argv[1] = "2048"
import sys

# Será utilizado para transformar o resultado do Python
# em JSON para que o Node.js consiga interpretar.
import json

# ============================================================
# CONFIGURAÇÕES DO SENSOR SIMULADO
# ============================================================

# O sensor utilizado como referência é o MH-Z19B.
CO2_MIN = 0
CO2_MAX = 5000

# ============================================================
# CONFIGURAÇÕES DO ADC
# ============================================================

# O ADC do STM32 possui 12 bits = 4095 valores.
ADC_MIN = 0
ADC_MAX = 4095

# ============================================================
# DADOS DE TREINAMENTO
# ============================================================

# X representa os valores de CO2 utilizados para treinar a Árvore de Decisão.
# Cada valor possui uma classificação correspondente no vetor "y".
# Estamos utilizando 25 exemplos de treinamento.

X = [
    [400],
    [500],
    [600],
    [700],
    [800],

    [900],
    [1000],
    [1100],
    [1200],
    [1300],

    [1400],
    [1500],
    [1600],
    [1700],
    [1800],

    [1900],
    [2000],
    [2200],
    [2400],
    [2600],

    [2800],
    [3200],
    [4000],
    [4500],
    [5000]
]


# ============================================================
# CLASSES DE QUALIDADE
# ============================================================

y = [
    0, #       0 = Excelente
    0, #       0 = Excelente
    0, #       0 = Excelente
    0, #       0 = Excelente
    0, #       0 = Excelente

    1, #       1 = Boa
    1, #       1 = Boa
    1, #       1 = Boa
    1, #       1 = Boa
    1, #       1 = Boa

    2, #       2 = Moderada
    2, #       2 = Moderada
    2, #       2 = Moderada
    2, #       2 = Moderada
    2, #       2 = Moderada

    3, #       3 = Ruim
    3, #       3 = Ruim
    3, #       3 = Ruim
    3, #       3 = Ruim
    3, #       3 = Ruim

    4, #       4 = Crítica
    4, #       4 = Crítica
    4, #       4 = Crítica
    4, #       4 = Crítica
    4  #       4 = Crítica
]

# ============================================================
# CRIAÇÃO DA ÁRVORE DE DECISÃO
# ============================================================

# Cria o modelo de Árvore de Decisão.
# A árvore irá aprender os padrões existentes
# nos dados X e y.
modelo = DecisionTreeClassifier()

# ============================================================
# TREINAMENTO DA ÁRVORE
# ============================================================

# Treina a árvore utilizando os dados definidos acima.
modelo.fit(X, y)

# ============================================================
# RECEBER O ADC
# ============================================================

# O Node.js executará o Python passando o ADC como argumento.
# Exemplo:
# py ClassificadorArvore.py 2048
# sys.argv[0] -> nome do arquivo
# sys.argv[1] -> valor ADC
adc = int(sys.argv[1])

# ============================================================
# VALIDAR O ADC
# ============================================================
# Garante que o ADC esteja dentro da faixa permitida pelo conversor de 12 bits.

if adc < ADC_MIN:
    adc = ADC_MIN

if adc > ADC_MAX:
    adc = ADC_MAX

# ============================================================
# CONVERSÃO ADC -> CO2
# ============================================================
# Regra de três.
# round = arredonda o valor para o inteiro mais próximo.
co2 = round((adc * CO2_MAX) / ADC_MAX)

# ============================================================
# CLASSIFICAÇÃO PELA ÁRVORE
# ============================================================
# Envia o valor de CO2 para a Árvore de Decisão.

classe = modelo.predict([[co2]])[0]

# ============================================================
# NOMES DAS CLASSES
# ============================================================
# Converte o número retornado pela árvore
# para um texto que será mostrado no sistema.

classes = {
    0: "Excelente",
    1: "Boa",
    2: "Moderada",
    3: "Ruim",
    4: "Critica"
}

# ============================================================
# PREPARAR RESULTADO
# ============================================================
# Cria um dicionário contendo os dados que serão
# enviados de volta para o Node.js.

resultado = {
    "adc": adc,
    "co2": co2,
    "qualidade": classes[classe]
}

# ============================================================
# ENVIAR RESULTADO PARA O NODE.JS
# ============================================================
# Converte o resultado para JSON.
# O Node.js receberá esse texto pelo stdout.

print(json.dumps(resultado))