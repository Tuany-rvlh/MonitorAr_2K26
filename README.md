🌱 MonitorAr 2K26

Sistema integrado de monitoramento e classificação da qualidade do ar utilizando STM32, C#, Node.js, Python e interface Web.

O MonitorAr 2K26 é um sistema desenvolvido para simular o monitoramento da qualidade do ar.

O projeto integra:

STM32F103C8 para aquisição dos dados;
USB CDC / Porta COM para comunicação;
C# como Gateway;
Node.js + Express como servidor e API REST;
Python + Machine Learning para classificação;
Interface Web para visualização dos resultados.

O projeto foi desenvolvido como parte do Projeto Integrado 2º Trimestre de 2026, envolvendo as disciplinas de Sistemas Embarcados (SEB), Linguagens de Programação (LPR), Desenvolvimento de Aplicativos (DAPL) e Inteligência Artificial (IA).

🎯 Objetivo

Desenvolver um sistema completo de:

aquisição de dados;
comunicação entre sistemas;
processamento;
classificação automática;
visualização das informações.

O projeto simula uma aplicação distribuída semelhante às utilizadas em sistemas de Internet das Coisas (IoT).

Fluxo principal
Sensor
  ↓
STM32
  ↓ USB CDC / Porta COM
Gateway C#
  ↓ HTTP / JSON
API Node.js + Express
  ↓
Python / IA
  ↓
Interface Web
🧩 Arquitetura do sistema

O sistema é dividido em 5 etapas principais:

```text
1. STM32F103C8
   ├── Leitura do sensor analógico
   ├── Filtro de média móvel
   └── Envio via USB CDC / Porta COM
            │
            ▼
2. Gateway C#
   ├── Recebe os dados da Porta COM
   ├── Processa e organiza as informações
   ├── Converte para JSON
   └── Envia via HTTP
            │
            ▼
3. Node.js + Express
   ├── API REST
   ├── Recebe e valida os dados
   ├── Encaminha para a IA
   └── Retorna a classificação
            │
            ▼
4. Python — Inteligência Artificial
   ├── Modelo Decision Tree
   └── Classifica as medições
            │
            ▼
5. Interface Web
   ├── Leitura atual
   ├── Classificação
   ├── Histórico
   ├── Estatísticas
   └── Estado do filtro
````

🔄 Comunicação
Etapa	Comunicação
STM32 → Gateway C#	USB CDC / Porta COM
Gateway C# → Node.js	HTTP / JSON
Node.js → Python	Chamada do classificador
Node.js → Interface Web	HTTP / dados Web
⚙️ Funcionamento
1. Aquisição de dados — STM32

O STM32F103C8 realiza a leitura de um sinal analógico utilizando o ADC.

Para simular o sensor, é utilizado um trimpot/potenciômetro.

O sistema também possui um botão para ativar ou desativar o filtro de média móvel.

O filtro utiliza 10 amostras para suavizar as variações da leitura.

As medições são enviadas periodicamente ao computador utilizando USB CDC, sendo reconhecidas como uma Porta COM.

2. Comunicação — Gateway C#

O Gateway desenvolvido em C# funciona como intermediário entre o STM32 e o servidor.

Responsabilidades:

receber as leituras da Porta COM;
interpretar os dados;
organizar as informações;
converter os dados para JSON;
enviar as medições para a API através de HTTP.
3. Servidor Web — Node.js

O servidor utiliza Node.js + Express para disponibilizar uma API REST.

Responsabilidades:

receber os dados enviados pelo Gateway;
validar as informações;
encaminhar os dados para a Inteligência Artificial;
receber a classificação;
retornar o resultado;
disponibilizar os dados para a interface Web.
4. Inteligência Artificial

A classificação é realizada utilizando Machine Learning baseado em Árvore de Decisão (Decision Tree).

O classificador:

recebe a leitura processada;
analisa o valor;
determina a categoria correspondente;
retorna o resultado para o servidor.

O modelo é executado pelo arquivo:

ClassificadorArvore.py
5. Interface Web

A interface apresenta os principais dados do sistema de forma visual.

São exibidos:

leitura atual;
valor do ADC;
valor convertido para CO₂;
classificação da qualidade do ar;
histórico das medições;
estado do filtro;
média;
valor máximo;
valor mínimo;
horário da última atualização;
indicador visual do nível de CO₂.
✨ Funcionalidades
Funcionalidades obrigatórias

Leitura de variável analógica

Aquisição utilizando STM32

Comunicação USB CDC

Comunicação através de Porta COM

Envio periódico das medições

Pré-processamento através de filtro

Filtro de média móvel

Gateway intermediário em C#

Conversão dos dados para JSON

Comunicação HTTP

API REST

Classificação utilizando Machine Learning

Interface Web

Exibição da leitura atual

Exibição da classificação

Histórico das medições

Indicação visual do estado atual

Funcionalidades adicionais
📊 Estatísticas das medições
📈 Histórico das leituras
🔎 Valores mínimo e máximo
📉 Cálculo de média
🎚️ Indicador visual do nível de CO₂
🔘 Indicação do estado do filtro
🛠️ Tecnologias utilizadas
Tecnologia	Utilização
C	Programação do STM32
STM32F103C8	Aquisição das medições
STM32CubeIDE	Desenvolvimento do firmware
USB CDC	Comunicação serial
C#	Gateway de comunicação
Node.js	Servidor Web
Express	API REST
Python	Classificação por IA
Scikit-learn	Machine Learning
HTML	Estrutura da interface
CSS	Estilização
JavaScript	Funcionamento da interface
JSON	Comunicação entre módulos
HTTP	Comunicação entre aplicações
Git/GitHub	Controle de versão
📁 Estrutura do projeto
MonitorAr_2K26/
│
├── ProjetoIntegrado_2K26/
│   │
│   ├── GatewayCSharp/
│   │   └── ...
│   │
│   ├── Hardware/
│   │   └── Medicao/
│   │       └── ...
│   │
│   ├── public/
│   │   ├── index.html
│   │   ├── app.js
│   │   └── ...
│   │
│   ├── ClassificadorArvore.py
│   ├── servidor.js
│   └── InfoServer.txt
│
├── TestePortaCOM/
│   ├── GatewayCSharp/
│   ├── simulador_serial.py
│   └── Requeriments.txt
│
├── package.json
├── package-lock.json
└── .gitignore
🚀 Como executar
Pré-requisitos

É necessário ter instalado:

STM32CubeIDE
.NET / Visual Studio
Node.js
Python 3
bibliotecas Python utilizadas pelo classificador
STM32F103C8
ambiente configurado para USB CDC
1. Clonar o repositório
git clone https://github.com/Tuany-rvlh/MonitorAr_2K26.git

Entre na pasta:

cd MonitorAr_2K26
2. Instalar as dependências

Na raiz do projeto:

npm install
3. Preparar o STM32

Abra o projeto no STM32CubeIDE e verifique:

configuração do ADC;
configuração da USB;
comunicação USB CDC;
botão do filtro;
conexão do trimpot;
compilação do firmware.

Depois, grave o firmware no STM32.

4. Conectar o STM32

Conecte o STM32 ao computador através da USB.

Verifique qual Porta COM foi atribuída ao dispositivo.

Essa porta deverá ser configurada no Gateway C#.

5. Iniciar o servidor

Execute:

node ProjetoIntegrado_2K26/servidor.js

O servidor ficará responsável por receber as requisições do Gateway.

6. Executar o Gateway C#

Abra:

ProjetoIntegrado_2K26/GatewayCSharp/

Configure a Porta COM correspondente ao STM32 e execute a aplicação.

O Gateway realizará continuamente:

Ler → Processar → Converter → Enviar
7. Acessar a interface

Com o servidor em execução, abra a interface Web pelo endereço disponibilizado pelo servidor.

A página apresentará as medições e os resultados da classificação.

🔄 Fluxo de uma medição
1. Trimpot altera o sinal analógico
          ↓
2. STM32 realiza a leitura
          ↓
3. Filtro é aplicado, se ativado
          ↓
4. STM32 envia via USB CDC
          ↓
5. Gateway C# recebe
          ↓
6. Dados são processados
          ↓
7. Dados são convertidos para JSON
          ↓
8. Gateway envia via HTTP
          ↓
9. API Node.js recebe
          ↓
10. Servidor chama a IA
          ↓
11. Decision Tree realiza a classificação
          ↓
12. Resultado retorna ao sistema
          ↓
13. Interface Web é atualizada
🔘 Filtro de média móvel

O sistema utiliza um filtro de média móvel com 10 amostras para reduzir oscilações nas medições.

Cálculo
Média = (A1 + A2 + A3 + ... + A10) / 10

O filtro pode ser ativado ou desativado através do botão conectado ao STM32.

A interface Web também indica o estado atual do filtro.

🤖 Classificação por Inteligência Artificial

O sistema utiliza uma Árvore de Decisão (Decision Tree) para classificar as medições.

Leitura
   ↓
Modelo de Machine Learning
   ↓
Classificação
   ↓
Interface Web

O objetivo é transformar os valores numéricos em uma classificação mais simples de interpretar.

📡 Comunicação entre os módulos
Origem	Destino	Comunicação
STM32	Gateway C#	USB CDC / Porta COM
Gateway C#	Node.js	HTTP
Gateway C#	Node.js	JSON
Node.js	Python	Execução do classificador
Node.js	Frontend	HTTP / dados Web
🧠 Decisões de implementação
STM32

Utilizado para realizar a aquisição do sinal analógico e o pré-processamento das medições.

C# como Gateway

Utilizado como intermediário entre o hardware e o servidor, realizando o tratamento da comunicação serial e o envio dos dados.

Node.js + Express

Utilizado para implementar a API REST e centralizar a comunicação entre os módulos.

Python

Utilizado na etapa de Inteligência Artificial, principalmente pela disponibilidade de ferramentas para Machine Learning.

JSON

Utilizado para estruturar as informações enviadas entre o Gateway e a API.

🧪 Testes

O projeto possui uma pasta específica para testes da comunicação serial:

TestePortaCOM/

Ela contém recursos para simulação e testes da comunicação pela Porta COM, permitindo testar partes do sistema sem utilizar diretamente o STM32.

🎥 Vídeo de apresentação

Vídeo:
🔗 Adicionar aqui o link do vídeo no YouTube.

O vídeo apresenta:

funcionamento do STM32;
comunicação entre os módulos;
classificação por IA;
funcionamento da interface Web.
📚 Projeto Integrado

O projeto integra conhecimentos das seguintes disciplinas:

Sistemas Embarcados (SEB)
Linguagens de Programação (LPR)
Desenvolvimento de Aplicativos (DAPL)
Inteligência Artificial (IA)

A proposta é desenvolver uma solução integrada de aquisição, comunicação, processamento, classificação e visualização de dados.

👥 Integrantes
Tuany Silva Pereira
Mariana Ferreira da Silva
📌 Status do projeto

🟢 Projeto concluído

O sistema integra:

Hardware + Comunicação Serial + Gateway C# + API REST + Inteligência Artificial + Interface Web

📄 Licença

Este projeto foi desenvolvido para fins educacionais, como parte das atividades do Projeto Integrado 2026.

🔗 Repositório

GitHub:
https://github.com/Tuany-rvlh/MonitorAr_2K26
