// Importa o Express, que será usado para criar
// o servidor e definir as rotas da API.
const express = require('express');

// Importa o execFile, que permite ao Node.js
// executar um programa externo.
// Neste projeto, será usado para executar o Python.
const { execFile } = require('child_process');

// Importa o módulo path, usado para montar
// caminhos de arquivos de forma correta.
// Será utilizado para encontrar o Dashboard.html.
const path = require('path');

// Cria uma aplicação utilizando o Express.
// "app" será usado para configurar o servidor,
// suas rotas e seus comportamentos.
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
// HISTORICO DAS MEDICOES
// ============================================================

// Guarda temporariamente as ultimas medicoes recebidas.
//
// Cada medicao armazenada possui:
// - ADC
// - AQI
// - qualidade do ar
// - estado do filtro
// - horario da medicao
let historico = [];


// ============================================================
// RECEBER MEDICAO DO C#
// ============================================================

// O C# envia uma requisicao HTTP POST para:
// http://localhost:3000/classificar
//
// O corpo da requisicao contem um JSON:
// {
//     "adc": 2048,
//     "filtro": false
// }

app.post('/classificar', (req, res) => {

    // Recupera o ADC enviado pelo C#.
    const adc = req.body.adc;

    // Recupera o estado do filtro enviado pelo C#.
    const filtro = req.body.filtro;

    // ========================================================
    // VALIDACAO DOS DADOS RECEBIDOS
    // ========================================================

    // Verifica se os dois campos foram enviados.
    if (adc === undefined || filtro === undefined) {

        return res.status(400).json({
            erro: "ADC ou filtro nao enviado"
        });
    }

    // Verifica se o ADC e um numero.
    // O ADC do STM32 possui 12 bits,
    // portanto seu valor deve estar entre 0 e 4095.
    if (typeof adc !== 'number' || adc < 0 || adc > 4095) 
    {
        return res.status(400).json({
            erro: "ADC invalido. Deve estar entre 0 e 4095"
        });

    }

    // Verifica se o filtro realmente recebeu
    // true ou false.
    if (typeof filtro !== 'boolean') {

        return res.status(400).json({ erro: "Filtro invalido. Deve ser true ou false"});

    }

    // ========================================================
    // EXECUTAR O PYTHON
    // ========================================================

    // Executa o arquivo ClassificadorArvore.py.
    // O ADC e enviado como argumento para o Python.
    //
    // Equivale a executar no terminal:
    // py ClassificadorArvore.py 2048
    //
    execFile(
        'py', ['ClassificadorArvore.py', String(adc)],

        (erro, stdout, stderr) => {

            // =================================================
            // VERIFICAR ERRO NA EXECUCAO DO PYTHON
            // =================================================

            if (erro) {

                console.log( "Erro ao executar Python:", erro);

                console.log("Saida de erro:", stderr);

                return res.status(500).json({
                    erro: "Erro ao executar o Python",
                    detalhes: erro.message
                });

            }

            // =================================================
            // CONVERTER RESPOSTA DO PYTHON
            // =================================================

            // O Python deve devolver um JSON.
            // Exemplo:
            // {
            //     "adc": 2048,
            //     "co2": 250,
            //     "qualidade": "Moderada"
            // }

            let respostaPython;

            try {

                // Transforma o texto recebido do Python
                // em um objeto que o Node.js consegue utilizar.
                respostaPython = JSON.parse(stdout);

            }
            catch (erroJSON) {

                // Caso o Python nao tenha retornado
                // um JSON valido, informa o erro.

                console.log(
                    "Erro: Python nao retornou um JSON valido."
                );

                console.log("Resposta recebida:", stdout);


                return res.status(500).json({erro: "Resposta invalida do Python"});

            }

            // =================================================
            // SALVAR MEDICAO NO HISTORICO
            // =================================================

            historico.push({

                // Valor ADC recebido.
                adc: respostaPython.adc,

                // Valor CO2 calculado pelo Python.
                co2: respostaPython.co2,

                // Classificacao da qualidade do ar.
                qualidade: respostaPython.qualidade,

                // Estado do filtro recebido do C#.
                filtro: filtro,

                // Horario em que a medicao foi recebida.
                horario: new Date()

            });

            // =================================================
            // LIMITAR O TAMANHO DO HISTORICO
            // =================================================

            // Mantem somente as ultimas 20 medicoes.
            // a mais antiga sera removida.
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
// ENVIAR HISTORICO PARA O DASHBOARD
// ============================================================
// O Dashboard pode fazer:
// GET http://localhost:3000/historico
// para receber todas as ultimas medicoes.
app.get('/historico', (req, res) => {
    res.json(historico);
});


// ============================================================
// ENVIAR ESTATISTICAS
// ============================================================
// O Dashboard pode fazer:
// GET http://localhost:3000/estatisticas
// para receber:
// - media
// - maior CO2
// - menor CO2

app.get('/estatisticas', (req, res) => {
    // Se ainda nao existem medicoes,
    // retorna um JSON vazio.

    if (historico.length === 0) {
        return res.json({});
    }

    // Cria um vetor contendo somente os valores de CO2.
    const valores = historico.map(
        item => item.co2
    );

    // Soma todos os valores de CO2
    // e divide pela quantidade de medicoes.
    const media =
        valores.reduce(
            (a, b) => a + b
        ) / valores.length;

    // Encontra o maior CO2 registrado.
    const maximo =
        Math.max(...valores);

    // Encontra o menor CO2 registrado.
    const minimo =
        Math.min(...valores);

    // Retorna as estatisticas em JSON.
    res.json({
        media: media.toFixed(2),
        maximo: maximo,
        minimo: minimo
    });

});

// ============================================================
// ABRIR O DASHBOARD
// ============================================================
// Quando o usuario acessar:
// http://localhost:3000/
// o Node.js abrira o arquivo:
// public/Dashboard.html

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname,'public','Dashboard.html'));
});

// ============================================================
// INICIAR SERVIDOR
// ============================================================

app.listen(port, () => {console.log( `Servidor rodando em http://localhost:${port}`);
    console.log(
        `Dashboard: http://localhost:${port}/`
    );

});