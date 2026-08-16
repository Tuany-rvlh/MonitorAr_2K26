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
# MH-Z19B, um sensor de CO2 baseado em tecnologia NDIR.
#
# Faixa utilizada nesta simulação:
#
#       0 ppm  -> 5000 ppm
#
# O trimpot representa essa faixa de concentração de CO2.
#
# O ADC do STM32 possui 12 bits:
#
#       0 -> 4095
#
# Portanto fazemos uma regra de três:
#
#       ADC 0    -> 0 ppm
#       ADC 4095 -> 5000 ppm
#
# Fórmula:
#
#       CO2 = (ADC * 5000) / 4095
#
# ============================================================


# ============================================================
# BIBLIOTECAS
# ============================================================

# Importa a Árvore de Decisão do Scikit-learn.
#
# Ela será utilizada para aprender a relação entre:
#
#       CO2 -> qualidade do ar
#
from sklearn.tree import DecisionTreeClassifier


# Importa sys.
#
# Será utilizado para receber o ADC enviado pelo Node.js.
#
# Exemplo:
#
# py ClassificadorArvore.py 2048
#
# Nesse caso:
#
# sys.argv[1] = "2048"
#
import sys


# Importa json.
#
# Será utilizado para transformar o resultado do Python
# em JSON para que o Node.js consiga interpretar.
#
import json


# ============================================================
# CONFIGURAÇÕES DO SENSOR SIMULADO
# ============================================================

# O sensor utilizado como referência é o MH-Z19B.
#
# Para esta simulação estamos utilizando a faixa:
#
#       0 a 5000 ppm de CO2
#
# O valor não está sendo medido por um MH-Z19B real.
# O trimpot/ADC está simulando essa medição.

CO2_MIN = 0

CO2_MAX = 5000


# ============================================================
# CONFIGURAÇÕES DO ADC
# ============================================================

# O ADC do STM32 possui 12 bits.
#
# Com 12 bits temos:
#
#       2^12 = 4096 valores
#
# Como começamos contando pelo zero:
#
#       menor valor = 0
#       maior valor = 4095

ADC_MIN = 0

ADC_MAX = 4095


# ============================================================
# DADOS DE TREINAMENTO
# ============================================================

# X representa os valores de CO2 utilizados para treinar
# a Árvore de Decisão.
#
# Cada valor possui uma classificação correspondente
# no vetor "y".
#
# Exemplo:
#
# X = [500]
# y = 0
#
# significa:
#
# 500 ppm -> classe 0
#
#
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

# O vetor y informa para a Árvore de Decisão
# qual classe pertence a cada valor de X.
#
# Classes utilizadas:
#
#       0 = Excelente
#       1 = Boa
#       2 = Moderada
#       3 = Ruim
#       4 = Crítica


y = [

    0,
    0,
    0,
    0,
    0,

    1,
    1,
    1,
    1,
    1,

    2,
    2,
    2,
    2,
    2,

    3,
    3,
    3,
    3,
    3,

    4,
    4,
    4,
    4,
    4

]


# ============================================================
# CRIAÇÃO DA ÁRVORE DE DECISÃO
# ============================================================

# Cria o modelo de Árvore de Decisão.
#
# A árvore irá aprender os padrões existentes
# nos dados X e y.

modelo = DecisionTreeClassifier(
    random_state=42
)


# ============================================================
# TREINAMENTO DA ÁRVORE
# ============================================================

# Treina a árvore utilizando os dados definidos acima.
#
# X = valores de CO2
#
# y = classificação correspondente

modelo.fit(X, y)


# ============================================================
# RECEBER O ADC
# ============================================================

# O Node.js executará o Python passando o ADC
# como argumento.
#
# Exemplo:
#
# py ClassificadorArvore.py 2048
#
# sys.argv[0] -> nome do arquivo
# sys.argv[1] -> valor ADC


adc = int(sys.argv[1])


# ============================================================
# VALIDAR O ADC
# ============================================================

# Garante que o ADC esteja dentro da faixa
# permitida pelo conversor de 12 bits.
#
# Se receber um valor menor que 0,
# utiliza 0.
#
# Se receber um valor maior que 4095,
# utiliza 4095.


if adc < ADC_MIN:

    adc = ADC_MIN


if adc > ADC_MAX:

    adc = ADC_MAX


# ============================================================
# CONVERSÃO ADC -> CO2
# ============================================================

# Agora fazemos a regra de três.
#
# Temos:
#
#       0 ADC    -> 0 ppm
#       4095 ADC -> 5000 ppm
#
#
# Fórmula:
#
#       CO2 = ADC * 5000 / 4095
#
#
# Exemplo:
#
#       ADC = 2048
#
#       CO2 = 2048 * 5000 / 4095
#
#       CO2 ≈ 2501 ppm
#
#
# Assim, o valor do trimpot pode representar
# qualquer concentração entre 0 e 5000 ppm.


co2 = round(
    (adc * CO2_MAX) / ADC_MAX
)


# ============================================================
# CLASSIFICAÇÃO PELA ÁRVORE
# ============================================================

# Envia o valor de CO2 para a Árvore de Decisão.
#
# A árvore analisa o valor recebido e retorna
# uma das cinco classes:
#
#       0
#       1
#       2
#       3
#       4


classe = modelo.predict(
    [[co2]]
)[0]


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
#
# Exemplo:
#
# {
#     "adc": 2048,
#     "co2": 2501,
#     "qualidade": "Moderada"
# }


resultado = {

    "adc": adc,

    "co2": co2,

    "qualidade": classes[classe]

}


# ============================================================
# ENVIAR RESULTADO PARA O NODE.JS
# ============================================================

# Converte o resultado para JSON.
#
# O Node.js receberá esse texto pelo stdout.
#
# Exemplo de saída:
#
# {"adc":2048,"co2":2501,"qualidade":"Moderada"}


print(
    json.dumps(resultado)
)