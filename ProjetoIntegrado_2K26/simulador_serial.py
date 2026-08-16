"""
====================================================================
 SIMULADOR DE SENSOR MQ-135 (STM32 VIRTUAL)
====================================================================

Este script substitui temporariamente o STM32F103C8 (Blue Pill).

Ele gera pacotes binarios IDENTICOS aos que o firmware real ira
enviar, e escreve esses pacotes em uma porta COM virtual (com0com),
com0com é um programa que cria portas seriais virtuais no computador.

Objetivo pedagogico: permitir testar TODO o pipeline (C# -> Node ->
Python -> HTML) antes de ligar o hardware fisico.

Dependencia:
    pip install pyserial

====================================================================
"""

import serial  # biblioteca pyserial: abre e escreve em portas seriais
import time  # controla o intervalo entre cada envio
import random  # gera ruido/variacao, simulando um sensor real
import sys  # permite encerrar o script com um codigo de erro


# -------------------------------------------------------------
# CONFIGURACAO DO SIMULADOR
# -------------------------------------------------------------

# Se o par de portas virtuais mudar (ex: COM5/COM6 -> COM7/COM8),
# só é necessario editar a linha abaixo. Nenhuma outra parte do
# script depende do nome da porta.

PORTA_VIRTUAL = "COM5"  # ponta do par virtual usada pelo simulador

BAUD_RATE = 115200
# o baud rate é a velocidade/configuração usada na comunicação serial.
# deve ser IGUAL ao configurado no Program.cs para que a comunicação funcione.

INTERVALO_ENVIO_SEGUNDOS = 1.0
# tempo entre cada leitura simulada

# -------------------------------------------------------------
# CONSTANTES DO PROTOCOLO
# (devem casar com Program.cs)
# -------------------------------------------------------------

BYTE_START = 0xAA
# marca o inicio de um pacote valido

VERSAO_PROTOCOLO = 0x01
# versao do protocolo (permite evoluir no futuro)

TIPO_LEITURA_SENSOR = 0x02
# tipo de mensagem: leitura de sensor

BYTE_FIM = 0xCC
# marca o fim de um pacote valido


# -------------------------------------------------------------
# CALCULO DO CHECKSUM
# -------------------------------------------------------------

def calcular_checksum(versao, tipo, filtro, adc_alto, adc_baixo):
    """
    Soma os bytes de dados (1 a 5 do pacote) e mantem apenas o byte
    menos significativo.

    Esse calculo precisa ser IDENTICO ao que o C# faz em
    ValidarPacote(), senao todo pacote sera rejeitado.
    """

    soma = (
        versao
        + tipo
        + filtro
        + adc_alto
        + adc_baixo
    )

    return soma & 0xFF
    # pega só os últimos 8 bits da soma.
    # Exemplo: se soma = 300, 300 em binário termina em 00101100.
    # Os últimos 8 bits correspondem a 44, então o checksum será 44 (0x2C).


# -------------------------------------------------------------
# MONTAGEM DO PACOTE
# -------------------------------------------------------------

def montar_pacote(valor_adc, filtro_ativo):
    """
    Monta um pacote binario de 8 bytes seguindo o protocolo
    proprietario:

    [START][VERSAO][TIPO][FILTRO][ADC_H][ADC_L][CHECKSUM][FIM]
    """

    # Garante que o valor do ADC esteja dentro da faixa permitida.
    # Como o ADC possui 12 bits, ele pode ter valores de 0 até 4095.
    #
    # Exemplos:
    # - Se valor_adc = -50, ele vira 0.
    # - Se valor_adc = 300, continua 300.
    # - Se valor_adc = 5000, ele vira 4095.
    valor_adc = max(0, min(4095, valor_adc))


    # Separa o valor do ADC em duas partes para poder enviá-lo pelo protocolo.
    # Cada byte consegue guardar apenas valores de 0 até 255.
    #
    # Exemplo:
    # ADC = 300
    # O valor 300 precisa ser dividido em:
    # byte alto  = 1
    # byte baixo = 44
    #
    # O >> 8 desloca o número 8 posições para a direita,
    # deixando apenas a parte "de cima" do valor.
    # O & 0xFF garante que o resultado fique limitado a 1 byte (0 a 255).
    adc_alto = (valor_adc >> 8) & 0xFF


    # Pega somente a parte "de baixo" do valor do ADC.
    # O & 0xFF mantém apenas os últimos 8 bits, ou seja, 1 byte.
    #
    # Exemplo:
    # ADC = 300
    # byte baixo = 44
    #
    # Assim, o valor 300 é enviado como dois bytes:
    # byte alto  = 1
    # byte baixo = 44
    #
    # Quando o C# receber esses dois bytes, ele poderá juntá-los
    # novamente para recuperar o valor original: 300.
    adc_baixo = valor_adc & 0xFF


    # 1 = filtro ligado
    # 0 = filtro desligado
    filtro_byte = 0x01 if filtro_ativo else 0x00


    # Calcula o checksum do pacote
    checksum = calcular_checksum(
        VERSAO_PROTOCOLO,
        TIPO_LEITURA_SENSOR,
        filtro_byte,
        adc_alto,
        adc_baixo
    )


    # Monta o pacote final com exatamente 8 bytes
    pacote = bytes([
        BYTE_START,           # 0xAA - inicio
        VERSAO_PROTOCOLO,     # 0x01 - versao
        TIPO_LEITURA_SENSOR,  # 0x02 - tipo: leitura de sensor
        filtro_byte,          # 0x00 ou 0x01 - estado do filtro
        adc_alto,             # byte alto do ADC
        adc_baixo,            # byte baixo do ADC
        checksum,             # byte de checagem
        BYTE_FIM              # 0xCC - fim
    ])


    return pacote


# -------------------------------------------------------------
# SIMULACAO DA LEITURA DO MQ-135
# -------------------------------------------------------------

def simular_leitura_mq135(valor_anterior):
    """
    Simula uma leitura de MQ-135 com variacao suave ao longo do tempo,
    em vez de numeros totalmente aleatorios e sem relacao entre si.

    Isso imita melhor o comportamento real de um sensor de gas,
    que muda aos poucos e nao "pula" de um extremo a outro a cada
    leitura.
    """

    # Quanto a leitura pode mudar desta vez
    variacao = random.randint(-150, 150)


    # Pequeno ruido eletrico simulado
    ruido_fino = random.randint(-20, 20)


    # Aplica a variacao ao valor anterior
    novo_valor = valor_anterior + variacao + ruido_fino


    # Limita a faixa de 12 bits: 0 a 4095
    return max(0, min(4095, novo_valor))


# -------------------------------------------------------------
# ENVIO DOS PACOTES
# -------------------------------------------------------------

def enviar_pacotes():
    """
    Loop principal do simulador.

    Abre a porta serial virtual, gera leituras continuas e envia
    pacotes no formato do protocolo.

    Tambem imprime cada pacote em hexadecimal para conferencia visual.
    """

    # Estado inicial do filtro
    filtro_ativo = False


    # Valor inicial simulado do ADC
    # 2000 esta aproximadamente no meio da escala de 0 a 4095
    valor_atual = 2000


    try:

        # Abre a porta COM5
        #
        # A porta COM5 e uma das pontas do par criado pelo com0com.
        # A outra ponta (COM6) sera utilizada pelo C#.
        with serial.Serial(
            PORTA_VIRTUAL,
            BAUD_RATE,
            timeout=1
        ) as porta:

            print(
                f"Simulador conectado em "
                f"{PORTA_VIRTUAL} @ {BAUD_RATE} baud"
            )

            print("Simulando STM32 + MQ-135...")

            print(
                "Pressione CTRL+C para encerrar.\n"
            )


            contador = 0


            # Loop infinito de simulacao
            while True:

                # Gera a proxima leitura simulada do MQ-135
                valor_atual = simular_leitura_mq135(valor_atual)


                # Monta o pacote seguindo o protocolo proprietario
                pacote = montar_pacote(valor_atual,filtro_ativo)


                # Envia o pacote pela porta virtual e so, envia bytes, nao strings, seguindo o protocolo.
                porta.write(pacote)


                # Converte o pacote para hexadecimal
                # para facilitar a conferencia, ou seja, visualizar o que esta sendo enviado.
                hexstr = pacote.hex(" ").upper()


                # Mostra no terminal:
                # numero da leitura
                # valor ADC
                # estado do filtro
                # pacote hexadecimal
                print(
                    f"[{contador:04d}] "
                    f"ADC={valor_atual:4d}  "
                    f"filtro={filtro_ativo}  "
                    f"pacote={hexstr}"
                )


                contador += 1


                # A cada 10 leituras,
                # alterna o estado do filtro
                if contador % 10 == 0:

                    filtro_ativo = not filtro_ativo

                    print(
                        f"--- Alternando filtro para: "
                        f"{filtro_ativo} ---"
                    )


                # Aguarda antes do proximo envio
                time.sleep(
                    INTERVALO_ENVIO_SEGUNDOS
                )


    except serial.SerialException as erro:

        # Erro tipico:
        # - porta nao existe
        # - porta ja esta em uso
        # - par virtual nao foi criado
        # - problema com o com0com

        print(
            f"ERRO: nao foi possivel abrir "
            f"{PORTA_VIRTUAL}: {erro}"
        )

        print(
            "Verifique se o com0com esta instalado "
            "e se o par de portas existe."
        )

        sys.exit(1)


    except KeyboardInterrupt:

        # Executado quando o usuario pressiona CTRL+C
        print(
            "\nSimulador encerrado pelo usuario."
        )


# -------------------------------------------------------------
# INICIO DO PROGRAMA
# -------------------------------------------------------------
# Verifica se este arquivo foi executado diretamente pelo Python.
# Se foi, inicia a função principal do simulador, que abre a porta COM,
# gera os valores do sensor e envia os pacotes continuamente.

if __name__ == "__main__":
    enviar_pacotes()