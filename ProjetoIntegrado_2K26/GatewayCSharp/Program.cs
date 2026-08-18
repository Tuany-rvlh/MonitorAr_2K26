using System;
// Permite usar recursos básicos do C#, como: Console, Exception, int, bool, etc.

using System.IO.Ports;
// Permite trabalhar com portas seriais COM.

using System.Net.Http;
// Permite fazer comunicação HTTP.

using System.Text;
// Permite trabalhar com codificação de texto.
// É usado para transformar o JSON em UTF-8 antes de enviá-lo para a API.

using System.Text.Json;
// Permite transformar objetos C# em JSON.

using System.Threading;
// Permite controlar o tempo de execução do programa.
// Neste projeto é usado principalmente com Thread.Sleep() para esperar alguns segundos antes de tentar conectar
// novamente a uma porta COM.

// ============================================================
// CONFIGURACOES GERAIS
// ============================================================

// A porta COM NÃO é mais fixa no código 
// O baudRate continua fixo pois precisa ser IGUAL ao configurado no STM32/simulador.
int baudRate = 115200;

// Endereco da API Node.js que recebera os dados.
string enderecoAPI = "http://localhost:3000/classificar";

// Tamanho fixo do pacote do protocolo proprietario.
// Exemplo de pacote: AA 01 02 00 07 D0 DA CC
const int TAMANHO_PACOTE = 8;

// Para cada porta, o C# pode tentar receber até 2 pacotes para descobrir se aquela porta é a correta.
// O valor 2 NÃO significa testar apenas 2 portas.
const int TENTATIVAS_LEITURA_TESTE = 2;

// Se o C# abrir uma porta e nenhum pacote válido chegar durante esse tempo, ele para de esperar e testa outra porta.
const int TIMEOUT_LEITURA_TESTE_MS = 1500;

// Versão do protocolo proprietario definido para o projeto.
const byte VERSAO_PROTOCOLO = 0x01;

// Tipo de mensagem definido para o projeto
const byte TIPO_MENSAGEM = 0x02;

// Inicio do protocolo proprietario definido para o projeto.
const byte INICIO_PROTOCOLO = 0xAA;

// Fim do protocolo proprietario definido para o projeto.
const byte FIM_PROTOCOLO = 0xCC;

// Cliente HTTP reaproveitado durante todo o programa. Permite conversar com o Node.js
HttpClient client = new HttpClient();

Console.WriteLine("==========================================");
Console.WriteLine(" Monitor de Qualidade do Ar");
Console.WriteLine(" Gateway C# - Deteccao automatica de porta");
Console.WriteLine("==========================================");

// ============================================================
// LOOP PRINCIPAL
// ============================================================

// O programa fica executando continuamente.
// Caso a comunicacao seja perdida, ele tenta encontrar novamente a porta automaticamente.
while (true)
{
    // Cria uma variável para guardar a porta COM que será encontrada.
    // O "?" significa que ela pode começar sem nenhuma porta definida (null).
    SerialPort? porta = null;

    try // ele tenta executar o código abaixo, mas se houver algum erro, ele pula para o catch.
    {
        // Procura automaticamente uma porta que esteja enviando pacotes válidos do nosso protocolo.
        porta = DetectarPortaSTM32(baudRate);

        Console.WriteLine($"Porta {porta.PortName} conectada e validada.");
        Console.WriteLine("Recebendo dados continuamente...\n");

        // Continua lendo enquanto a porta estiver aberta.
        while (porta.IsOpen)
        {
            try // ele tenta executar o código abaixo, mas se houver algum erro, ele pula para o catch.
            {
                // Le exatamente um pacote de 8 bytes.
                byte[] pacote = LerPacote(porta);

                // Mostra o pacote recebido em hexadecimal.
                Console.WriteLine($"HEX recebido: {BitConverter.ToString(pacote).Replace("-", " ")}");

                // Verifica se o pacote segue o protocolo.
                if (!ValidarPacote(pacote))
                {
                    Console.WriteLine("ERRO: pacote invalido, descartando.");
                    Console.WriteLine();

                    // Ignora o pacote e tenta ler o proximo.
                    // O continue faz o programa voltar para o início do loop e esperar o próximo pacote.  
                    continue;
                }

                // Extrai o valor do ADC.
                int adc = ExtrairADC(pacote);

                // Extrai o estado do filtro.
                bool filtro = ExtrairFiltro(pacote);

                Console.WriteLine($"ADC: {adc}");

                if (filtro)
                    Console.WriteLine("Filtro: ATIVADO");
                else
                    Console.WriteLine("Filtro: DESATIVADO");

                // Converte os dados para JSON.
                string json = ConverterParaJson(adc, filtro);

                Console.WriteLine($"JSON: {json}");

                // Envia o JSON para a API Node.js.
                // await faz o programa esperar a resposta da API antes de continuar.
                _  = EnviarAPI(client, enderecoAPI, json);

                Console.WriteLine();
            }
            catch (TimeoutException)
            {
                // Nenhum byte chegou dentro do tempo configurado.
                Console.WriteLine("ERRO: tempo de espera excedido aguardando dados.");
                Console.WriteLine();
            }
            catch (HttpRequestException erroHttp)
            {
                // O servidor Node.js pode estar desligado ou o endereco da API pode estar incorreto.
                Console.WriteLine($"ERRO: falha ao conectar na API ({erroHttp.Message}).");
                Console.WriteLine("Verifique se o servidor Node.js esta rodando.");
                Console.WriteLine();
            }
            catch (IOException erroIO)
            {
                // A comunicacao serial foi perdida. Isso pode acontecer se o dispositivo for desconectado.
                Console.WriteLine($"ERRO: perda de comunicacao com a porta serial: {erroIO.Message}");
                Console.WriteLine("Tentando reconectar...\n");

                // Sai do loop da porta e volta para a deteccao.
                break;
            }
        }
    }

    catch (Exception erroGeral)
    {
        // Trata erros inesperados durante a conexao.
        Console.WriteLine($"ERRO INESPERADO: {erroGeral.Message}");
        Console.WriteLine("Nova tentativa em 3 segundos...\n");
    }

    finally
    {
        // O finally sempre é executado, mesmo quando ocorre um erro.
        // Aqui garantimos que a porta seja fechada para não ficar ocupada.
        if (porta is { IsOpen: true })
        {
            porta.Close();
        }
    }

    // Aguarda antes de tentar encontrar uma porta novamente.
    Thread.Sleep(3000);
}

// ============================================================
// DETECCAO AUTOMATICA DE PORTA COM
// ============================================================
// o programa procura todas as portas disponíveis.
// Ele testa cada porta e procura por um pacote que corresponda ao nosso protocolo.

// IMPORTANTE:
// O com0com pode retornar entradas como CNCA0 e CNCB0.
// Essas entradas nao sao portas COM utilizaveis pelo
// System.IO.Ports, portanto elas sao ignoradas.

// Procura automaticamente uma porta COM válida.
// "static" permite usar a função diretamente.
// "SerialPort" indica que ela retorna a porta encontrada.
// "baudRate" recebe a velocidade da comunicação serial.
static SerialPort DetectarPortaSTM32(int baudRate)
{
    while (true)
    {
        // Obtém todas as portas seriais encontradas pelo sistema.
        string[] portasDisponiveis = SerialPort.GetPortNames();

        if (portasDisponiveis.Length == 0)
        {
             // Informa que nenhuma porta foi encontrada
            Console.WriteLine("Nenhuma porta COM encontrada. Aguardando dispositivo...");

            // Espera 2 segundos antes de procurar novamente, evitando que o programa fique procurando sem parar.
            Thread.Sleep(2000);

            // Volta para o início do while e faz uma nova busca pelas portas.
            continue;
        }

        Console.WriteLine($"Portas encontradas: {string.Join(", ", portasDisponiveis)}");

        // Testa cada entrada encontrada.
        foreach (string nomePorta in portasDisponiveis)
        {
            // ====================================================
            // CORRECAO PARA O COM0COM
            // ====================================================
            // Como nosso programa precisa trabalhar com COM3,
            // COM4, COM5, COM6 etc., ignoramos qualquer entrada
            // que nao comece com "COM".

            if (!nomePorta.StartsWith("COM", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine(
                    $"  {nomePorta}: ignorada, nao e uma porta COM utilizavel."
                );

                // Volta para o início do while e faz uma nova busca pelas portas.
                continue;
            }

            // Cria uma variável para guardar temporariamente a porta que está sendo testada.
            // Ela começa como "null" porque nenhuma porta foi escolhida ainda.
            // Cada porta encontrada (COM3, COM4, COM5...) será colocada nessa variável
            // enquanto o programa verifica se ela é a porta correta
            SerialPort? candidata = null;

            try // ele tenta executar o código abaixo, mas se houver algum erro, ele pula para o catch.
            {
                // Cria uma porta serial candidata.
                candidata = new SerialPort(nomePorta, baudRate)
                {
                    // Impede que o programa fique travado esperando dados indefinidamente.
                    ReadTimeout = TIMEOUT_LEITURA_TESTE_MS
                };

                // Tenta abrir a porta.
                candidata.Open();

                // Verifica se a porta esta realmente enviando pacotes validos do nosso protocolo.
                if (ValidarComoOrigemDoProtocolo(candidata))
                {
                    // Encontramos a porta correta. Ela permanece aberta.
                    return candidata;
                }

                // A porta abriu, mas nao enviou um pacote valido.
                candidata.Close();
            }
            catch (UnauthorizedAccessException)
            {
                // A porta ja esta sendo utilizada por outro programa.
                Console.WriteLine($"  {nomePorta}: em uso por outro processo, pulando.");
            }
            catch (IOException)
            {
                // A porta existe, mas nao foi possível utiliza-la.
                Console.WriteLine($"  {nomePorta}: nao foi possível abrir, pulando.");
            }
            catch (TimeoutException)
            {
                // A porta abriu, mas nao recebeu um pacote válido dentro do tempo configurado.
                Console.WriteLine($"  {nomePorta}: nenhum dado válido recebido, pulando.");

                candidata?.Close();
            }
        }

        // Nenhuma porta foi validada nesta rodada.
        Console.WriteLine(
            "Nenhuma porta validada nesta rodada. Tentando de novo em 3s...\n"
        );

        Thread.Sleep(3000);
    }
}

// ============================================================
// VALIDACAO DA ORIGEM DO PROTOCOLO
// ============================================================
// Le algumas amostras da porta e verifica se elas correspondem ao nosso protocolo proprietario.
static bool ValidarComoOrigemDoProtocolo(SerialPort porta)
{
    for (int tentativa = 0; tentativa < TENTATIVAS_LEITURA_TESTE; tentativa++)
    {
        // Tenta ler um pacote completo.
        byte[] pacoteTeste = LerPacote(porta);

        // Verifica se o pacote segue o protocolo.
        if (ValidarPacote(pacoteTeste))
        {
            return true;
        }
    }

    // Nenhuma tentativa produziu um pacote valido.
    return false;
}

// ============================================================
// LER PACOTE
// ============================================================
// O nosso protocolo possui exatamente 8 bytes:
// Portanto, o C# precisa receber exatamente 8 bytes.
static byte[] LerPacote(SerialPort porta)
{
    // Procura o byte inicial do protocolo: AA
    while (true)
    {
        int primeiroByte = porta.ReadByte();

        if (primeiroByte == INICIO_PROTOCOLO)
        {
            break;
        }
    }

    // Já encontramos o AA.
    // Cria um buffer para armazenar os 8 bytes.
    byte[] pacote = new byte[TAMANHO_PACOTE];

    pacote[0] = INICIO_PROTOCOLO;
    // Quantidade de bytes que ja foram recebidos.
    int totalLido = 1;

    // Continua lendo ate completar os 8 bytes.
    while (totalLido < TAMANHO_PACOTE)
    {
        // Leia os bytes que chegaram e coloque-os no lugar certo dentro de pacote.
        int quantidade = porta.Read(pacote, totalLido, TAMANHO_PACOTE - totalLido);
        // "pacote" = onde os bytes serão armazenados.
        // "totalLido" = posição onde devemos começar a guardar.
        // "TAMANHO_PACOTE - totalLido" = quantidade de bytes que ainda faltam.

        totalLido += quantidade;
    }
    return pacote;
}

// ============================================================
// VALIDAR PACOTE
// ============================================================
// Verifica se o pacote recebido segue exatamente o protocolo
static bool ValidarPacote(byte[] pacote)
{
    // 1. Tamanho
    if (pacote.Length != TAMANHO_PACOTE)
    {
        Console.WriteLine(
            "ERRO: tamanho do pacote incorreto."
        );

        return false;
    }

    // 2. Byte de inicio
    if (pacote[0] != INICIO_PROTOCOLO)
    {
        Console.WriteLine(
            "ERRO: inicio do pacote incorreto."
        );

        return false;
    }
    
    // 3. Versao do protocolo
    if (pacote[1] != VERSAO_PROTOCOLO)
    {
        Console.WriteLine(
            "ERRO: versao do protocolo inválida."
        );

        return false;
    }

    // 4. Tipo de mensagem
    if (pacote[2] != TIPO_MENSAGEM)
    {
        Console.WriteLine(
            "ERRO: tipo de mensagem inválido."
        );

        return false;
    }

    // 5. Estado do filtro
    // 0x00 = desativado
    // 0x01 = ativado
    if (pacote[3] != 0x00 && pacote[3] != 0x01)
    {
        Console.WriteLine(
            "ERRO: estado do filtro inválido."
        );

        return false;
    }

    // 6. Checksum
    // O checksum e calculado somando: versao + tipo + filtro + ADC_H + ADC_L
    // e mantendo apenas os 8 bits menos significativos.
    byte checksumCalculado =
        (byte)(
            pacote[1]
            + pacote[2]
            + pacote[3]
            + pacote[4]
            + pacote[5]
        );

    // Compara o checksum calculado com o recebido.
    if (pacote[6] != checksumCalculado)
    {
        Console.WriteLine(
            $"ERRO: checksum inválido. " +
            $"Recebido: {pacote[6]:X2}, " +
            $"calculado: {checksumCalculado:X2}"
        );

        return false;
    }

    // 7. Byte de fim
    if (pacote[7] != FIM_PROTOCOLO)
    {
        Console.WriteLine(
            "ERRO: fim do pacote incorreto."
        );

        return false;
    }

    // Se chegou até aqui, o pacote é válido.
    return true;
}

// ============================================================
// EXTRAIR ADC
// ============================================================
// ADC_H = byte alto
// ADC_L = byte baixo
//
// O C# junta os dois novamente (|) para recuperar o valor
// original entre 0 e 4095.
static int ExtrairADC(byte[] pacote)
{
    //Coloca ADC_H no byte alto e junto com ADC_L no byte baixo
    int adc = (pacote[4] << 8) | pacote[5];
    return adc;
}

// ============================================================
// EXTRAIR FILTRO
// ============================================================
// Retorna: true  = filtro ativado ou false = filtro desativado
static bool ExtrairFiltro(byte[] pacote)
{
    return pacote[3] == 0x01;
}

// ============================================================
// CONVERTER PARA JSON
// ============================================================
// Converte o ADC e o estado do filtro para JSON.
static string ConverterParaJson(int adc, bool filtro)
{
    // Cria os campos do JSON e coloca os valores recebidos neles.
    return JsonSerializer.Serialize(new
    {
        adc = adc,
        filtro = filtro
    });
}

// ============================================================
// ENVIAR PARA API
// ============================================================
// Envia o JSON para o servidor Node.js através de uma
// requisição HTTP POST.
static async Task<string> EnviarAPI(
    HttpClient client, // Cliente HTTP que será usado para enviar a requisição.
    string enderecoAPI, // Endereço da API que receberá os dados.
    string json) // JSON que será enviado na requisição.
{
    // Prepara o JSON para ser enviado na requisição.
    // UTF8 = forma de codificação do texto.
    // application/json = informa ao servidor que o conteúdo é JSON.
    using StringContent conteudo =
        new StringContent(json, Encoding.UTF8, "application/json");

    // Envia o JSON para o endereço da API.
    // Exemplo:
    // http://localhost:3000/classificar
    HttpResponseMessage resposta =
        await client.PostAsync(
            enderecoAPI, // URL da API que receberá os dados.
            conteudo // Conteúdo da requisição (JSON).
        );

    // Verifica se o servidor respondeu com um código
    // que indica sucesso (por exemplo, HTTP 200).
    if (!resposta.IsSuccessStatusCode)
    {
        // Se houve erro, retorna o código e a descrição
        // enviados pelo servidor.
        return
            $"API retornou erro: " +
            $"{(int)resposta.StatusCode} " +
            $"{resposta.ReasonPhrase}";
    }

    // Se deu certo, lê e retorna o conteúdo enviado
    // pelo servidor na resposta.
    return await resposta.Content.ReadAsStringAsync();
}
