// Importa o Express, que será usado para criar o servidor e definir as rotas da API.
const express = require('express');

// Importa o execFile, que permite ao Node.js executar um programa externo.
// Neste projeto, será usado para executar o Python.
const { execFile } = require('child_process');

// Importa o módulo path, usado para manipular caminhos de arquivos e diretórios.
// Será utilizado para encontrar o Dashboard.html.
const path = require('path');

// Cria uma aplicação utilizando o Express.
// "app" será usado para configurar o servidor, suas rotas e seus comportamentos.
const app = express();

// ============================================================
// CONFIGURACAO DO SERVIDOR
// ============================================================

// Porta onde o servidor Node.js ficará funcionando.
const port = 3000;

// Permite que o Node.js receba e interprete dados enviados no formato JSON.
app.use(express.json());

// Permite que o navegador acesse os arquivos que estão dentro da pasta "public".
app.use(express.static(path.join(__dirname, 'public')));

// ============================================================
// HISTÓRICO DE MEDIÇÕES
// ============================================================
// Guarda temporariamente as últimas medições recebidas.
// Cada medição armazenada possui: ADC, AQI, qualidade do ar, estado do filtro, horário da medição
let historico = [];

// Soma de todas as medições recebidas desde o início do sistema.
let somaEstatisticas = 0;

// Quantidade total de medições recebidas.
let quantidadeEstatisticas = 0;

// Maior valor já registrado.
let maiorEstatistica = null;

// Menor valor já registrado.
let menorEstatistica = null;
// ============================================================
// RECEBER MEDIÇÃO DO C#
// ============================================================
// O C# envia uma requisição HTTP POST para:
// http://localhost:3000/classificar

app.post('/classificar', (req, res) => {

    // Recupera o ADC enviado pelo C#.
    const adc = req.body.adc;

    // Recupera o estado do filtro enviado pelo C#.
    const filtro = req.body.filtro;

    // ========================================================
    // VALIDAÇÃO DOS DADOS RECEBIDOS
    // ========================================================

    // Verifica se os dois campos foram enviados.
    if (adc === undefined || filtro === undefined) 
    {
        return res.status(400).json({erro: "ADC ou filtro nao enviado"});
    }

    // Verifica se o ADC é um número.
    if (typeof adc !== 'number' || adc < 0 || adc > 4095) 
    {
        return res.status(400).json({erro: "ADC invalido. Deve estar entre 0 e 4095"});
    }

    // Verifica se o filtro realmente recebeu true ou false.
    if (typeof filtro !== 'boolean') {
        return res.status(400).json({ erro: "Filtro invalido. Deve ser true ou false"});
    }

    // ========================================================
    // EXECUTAR O PYTHON
    // ========================================================
    // Executa o arquivo ClassificadorArvore.py.
    // O ADC e enviado como argumento para o Python.
    // Equivale a executar no terminal:
    // py ClassificadorArvore.py 2048

    execFile(
        'py', ['ClassificadorArvore.py', String(adc)],

        (erro, stdout, stderr) => {
            // =================================================
            // VERIFICAR ERRO NA EXECUÇÃO DO PYTHON
            // =================================================
            if (erro) {

                console.log( "Erro ao executar Python:", erro);
                console.log("Saida de erro:", stderr);

                return res.status(500).json({erro: "Erro ao executar o Python", detalhes: erro.message});
            }

            // =================================================
            // CONVERTER RESPOSTA DO PYTHON
            // =================================================
            // O Python deve devolver um JSON.
            let respostaPython;

            try {

                // Transforma o texto recebido do Python em um objeto que o Node.js consegue utilizar.
                respostaPython = JSON.parse(stdout);
            }
            catch (erroJSON) {

                // Caso o Python nao tenha retornado um JSON válido, informa o erro.
                console.log("Erro: Python nao retornou um JSON valido.");
                console.log("Resposta recebida:", stdout);

                return res.status(500).json({erro: "Resposta invalida do Python"});

            }
            
            // ========================================================
            // ATUALIZAR ESTATÍSTICAS GERAIS
            // ========================================================

            const co2Atual = respostaPython.co2;

            // Adiciona o valor à soma total.
            somaEstatisticas += co2Atual;

            // Aumenta a quantidade de medições.
            quantidadeEstatisticas++;

            // Verifica se é o maior valor já registrado.
            if (maiorEstatistica === null || co2Atual > maiorEstatistica)
            {
                maiorEstatistica = co2Atual;
            }

            // Verifica se é o menor valor já registrado.
            if (menorEstatistica === null || co2Atual < menorEstatistica)
            {
                menorEstatistica = co2Atual;
            }
            
            // =================================================
            // SALVAR MEDIÇÃO NO HISTÓRICO
            // =================================================
            historico.push({
                // Valor ADC recebido.
                adc: respostaPython.adc,

                // Valor CO2 calculado pelo Python.
                co2: respostaPython.co2,

                // Classificação da qualidade do ar.
                qualidade: respostaPython.qualidade,

                // Estado do filtro recebido do C#.
                filtro: filtro,

                // Horário em que a medição foi recebida.
                horario: new Date()
            });

            // =================================================
            // LIMITAR O TAMANHO DO HISTÓRICO
            // =================================================
            // Mantem somente as ultimas 20 medicoes e a mais antiga será removida.
            if (historico.length > 20) {
                historico.shift();
            }

            // =================================================
            // ENVIAR RESULTADO DE VOLTA PARA O C#
            // =================================================
            // Retorna a resposta produzida pelo Python.
            res.json(respostaPython);
        }
    );

});

// ============================================================
// ENVIAR HISTÓRICO PARA O DASHBOARD
// ============================================================
// O Dashboard pode fazer: GET http://localhost:3000/historico para receber todas as ultimas medicoes.
app.get('/historico', (req, res) => {res.json(historico);});

// ============================================================
// ENVIAR ESTATISTICAS
// ============================================================
// O Dashboard pode fazer:
// GET http://localhost:3000/estatisticas para receber: media, maior CO2 e menor CO2

app.get('/estatisticas', (req, res) => {

    // Ainda não existem medições.
    if (quantidadeEstatisticas === 0)
    {
        return res.json({});
    }

    // Média de TODAS as medições desde o início.
    const media =
        somaEstatisticas / quantidadeEstatisticas;

    res.json({
        media: media.toFixed(2),
        maximo: maiorEstatistica,
        minimo: menorEstatistica
    });
});

// ============================================================
// ABRIR O DASHBOARD
// ============================================================
// Quando o usuario acessar: http://localhost:3000/
// o Node.js abrira o arquivo: public/Dashboard.html

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname,'public','Dashboard.html'));
});

// ============================================================
// INICIAR SERVIDOR
// ============================================================
app.listen(port, () => 
    {console.log( `Servidor rodando em http://localhost:${port}`);
});