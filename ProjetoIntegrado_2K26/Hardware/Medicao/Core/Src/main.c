/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "usbd_cdc_if.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* ==========================================================
 * PROTOCOLO PROPRIET�?RIO
 *
 * AA 01 02 FILTRO ADC_H ADC_L CHECKSUM CC
 *
 * Byte 0 = início
 * Byte 1 = versão
 * Byte 2 = tipo
 * Byte 3 = estado do filtro
 * Byte 4 = ADC alto
 * Byte 5 = ADC baixo
 * Byte 6 = checksum
 * Byte 7 = fim
 * ========================================================== */

#define BYTE_START             0xAA
#define VERSAO_PROTOCOLO       0x01
#define TIPO_LEITURA_SENSOR    0x02
#define BYTE_FIM               0xCC

#define TAMANHO_PACOTE         8

#define ADC_MIN                0
#define ADC_MAX                4095

#define TAMANHO_JANELA_MEDIA   5

#define CLICK_BOTAO  	HAL_GPIO_ReadPin(botaoFiltro_GPIO_Port, botaoFiltro_Pin)

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;

/* USER CODE BEGIN PV */
static uint16_t buffer_media[TAMANHO_JANELA_MEDIA] = {0};

static uint8_t indice_buffer = 0;

static uint8_t buffer_cheio = 0;

uint32_t ultimoEnvio = 0;

uint8_t filtro_ativo = 0;
uint8_t botaoAnterior = 1;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
/* USER CODE BEGIN PFP */
void MontarPacote(uint16_t valor_adc, uint8_t filtro_ativo, uint8_t *pacote);

void AdicionarAmostra(uint16_t nova_amostra);

uint16_t CalcularMediaMovel(void);

uint8_t LerBotao(void);

uint8_t CalcularChecksum(uint8_t versao, uint8_t tipo, uint8_t filtro, uint8_t adc_alto, uint8_t adc_baixo);


/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */



/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_ADC1_Init();
  MX_USB_DEVICE_Init();
  /* USER CODE BEGIN 2 */
  /* Estado atual do filtro */
  uint8_t filtro_ativo = 0;

  /* Pacote de transmissão */
  uint8_t pacote[TAMANHO_PACOTE];
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	  /* Verifica o botão continuamente */
	      if (LerBotao())
	      {
	          filtro_ativo = !filtro_ativo;

	          // Quando o filtro for ativado,
	             // começa uma nova janela de média.
	             if (filtro_ativo)
	             {
	                 indice_buffer = 0;
	                 buffer_cheio = 0;
	             }
	      }

	      /* A cada 1 segundo, faz uma nova leitura e envia para a porta COM */
	      if (HAL_GetTick() - ultimoEnvio >= 1000)
	      {
	          ultimoEnvio = HAL_GetTick();

	          HAL_ADC_Start(&hadc1);

	          if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK)
	          {
	              uint16_t leitura_bruta = HAL_ADC_GetValue(&hadc1);

	              /* Adiciona a leitura atual ao buffer */
	              AdicionarAmostra(leitura_bruta);

	              uint16_t valor_final;

	              if (filtro_ativo)
	              {
	                  valor_final = CalcularMediaMovel();
	              }
	              else
	              {
	                  valor_final = leitura_bruta;
	              }

	              /* Monta e envia o pacote */
	              MontarPacote(valor_final, filtro_ativo, pacote);

	              CDC_Transmit_FS(pacote, TAMANHO_PACOTE);
	          }

	          HAL_ADC_Stop(&hadc1);
	      }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC|RCC_PERIPHCLK_USB;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV6;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_PLL_DIV1_5;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */
  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_3;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_55CYCLES_5;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin : botaoFiltro_Pin */
  GPIO_InitStruct.Pin = botaoFiltro_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(botaoFiltro_GPIO_Port, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */


uint8_t CalcularChecksum(uint8_t versao, uint8_t tipo, uint8_t filtro, uint8_t adc_alto, uint8_t adc_baixo)
{
    uint16_t soma = versao + tipo + filtro + adc_alto + adc_baixo;

    return (uint8_t)(soma & 0xFF);
}

void MontarPacote(uint16_t valor_adc, uint8_t filtro_ativo, uint8_t *pacote)
{
    if (valor_adc > ADC_MAX)
    {
        valor_adc = ADC_MAX;
    }

    uint8_t adc_alto = (uint8_t)((valor_adc >> 8) & 0xFF);

    uint8_t adc_baixo = (uint8_t)(valor_adc & 0xFF);

    uint8_t filtro_byte = filtro_ativo ? 0x01 : 0x00;

    uint8_t checksum = CalcularChecksum(VERSAO_PROTOCOLO, TIPO_LEITURA_SENSOR, filtro_byte, adc_alto, adc_baixo);

    pacote[0] = BYTE_START;
    pacote[1] = VERSAO_PROTOCOLO;
    pacote[2] = TIPO_LEITURA_SENSOR;
    pacote[3] = filtro_byte;
    pacote[4] = adc_alto;
    pacote[5] = adc_baixo;
    pacote[6] = checksum;
    pacote[7] = BYTE_FIM;
}


void AdicionarAmostra(uint16_t nova_amostra)
{
    buffer_media[indice_buffer] = nova_amostra;

    indice_buffer++;

    if (indice_buffer >= TAMANHO_JANELA_MEDIA)
    {
        indice_buffer = 0;
        buffer_cheio = 1;
    }
}
uint16_t CalcularMediaMovel(void)
{
    uint32_t soma = 0;

    uint8_t quantidade = buffer_cheio ? TAMANHO_JANELA_MEDIA : indice_buffer;

    if (quantidade == 0)
    {
        return 0;
    }

    for (uint8_t i = 0; i < quantidade; i++)
    {
        soma += buffer_media[i];
    }

    return (uint16_t)(soma / quantidade);
}

uint8_t LerBotao(void)
{
	uint8_t estadoAtual = HAL_GPIO_ReadPin(botaoFiltro_GPIO_Port, botaoFiltro_Pin);

	    uint8_t clique = 0;

	    // Detecta apenas a transição:
	    // solto -> pressionado
	    if (botaoAnterior == 1 &&
	        estadoAtual == 0)
	    {
	    	HAL_Delay(200);
	        clique = 1;
	    }

	    botaoAnterior = estadoAtual;

	    return clique;
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
