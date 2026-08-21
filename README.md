🌱 MonitorAr 2K26

Sistema integrado de monitoramento e classificação da qualidade do ar utilizando STM32, C#, Node.js, Python e interface Web.

O MonitorAr 2K26 é um sistema distribuído desenvolvido para simular o monitoramento de uma variável relacionada à qualidade do ar. O projeto realiza a aquisição de dados por meio de um STM32F103C8, transmite as medições para um computador através de USB CDC / Porta COM, processa essas informações em uma aplicação intermediária desenvolvida em C#, envia os dados para uma API REST em Node.js e utiliza um modelo de Machine Learning em Python para realizar a classificação automática.

Os resultados são apresentados em uma interface Web, permitindo acompanhar a leitura atual, a classificação obtida e o histórico das medições.

O projeto foi desenvolvido como parte do Projeto Integrado 2º Trimestre de 2026, envolvendo as disciplinas de Sistemas Embarcados (SEB), Linguagens de Programação (LPR), Desenvolvimento de Aplicativos (DAPL) e Inteligência Artificial (IA).

🎯 Objetivo

O principal objetivo do MonitorAr é desenvolver uma solução completa de aquisição, comunicação, processamento, classificação e visualização de dados, simulando uma aplicação distribuída semelhante às utilizadas em sistemas de Internet das Coisas (IoT).

O sistema integra diferentes tecnologias para criar um fluxo completo:

Sensor → STM32 → USB/COM → C# → HTTP/JSON → API Node.js → IA Python → Interface Web

Dessa forma, uma leitura realizada no microcontrolador percorre todas as etapas do sistema até ser apresentada ao usuário.

🧩 Arquitetura do sistema
┌─────────────────────┐
│       STM32         │
│                     │
│  Leitura do ADC     │
│  Sensor / Trimpot   │
│  Filtro de média    │
└──────────┬──────────┘
           │
           │ USB CDC
           │ Porta COM
           ▼
┌─────────────────────┐
│   Gateway C#        │
│                     │
│ Leitura da COM      │
│ Tratamento dos dados│
│ Conversão para JSON │
└──────────┬──────────┘
           │
           │ HTTP / JSON
           ▼
┌─────────────────────┐
│   Servidor Node.js  │
│      Express        │
│                     │
│      API REST       │
└──────────┬──────────┘
           │
           │ Chamada
           ▼
┌─────────────────────┐
│ Inteligência        │
│ Artificial           │
│                     │
│ Decision Tree       │
│ Classificação       │
└──────────┬──────────┘
           │
           │ Resultado
           ▼
┌─────────────────────┐
│    Interface Web    │
│                     │
│ ADC / CO₂           │
│ Classificação       │
│ Histórico            │
│ Estatísticas        │
│ Estado do filtro    │
└─────────────────────┘
⚙️ Funcionamento
1. Aquisição de dados — STM32

O microcontrolador STM32F103C8 realiza a leitura de um sinal analógico utilizando o ADC.

Para a simulação do sensor, é utilizado um trimpot/potenciômetro, permitindo variar manualmente o valor de entrada.

A leitura é realizada pelo ADC e enviada periodicamente ao computador utilizando USB CDC, sendo reconhecida pelo sistema como uma Porta COM.

Além da leitura, o sistema possui um botão responsável pela ativação e desativação do filtro de média móvel.

O filtro utiliza uma janela de 10 amostras, permitindo suavizar variações rápidas na leitura.

2. Comunicação — Gateway C#

O Gateway desenvolvido em C# funciona como intermediário entre o STM32 e o servidor.

Suas principais responsabilidades são:

estabelecer comunicação com a Porta COM;
receber as leituras enviadas pelo STM32;
interpretar os dados recebidos;
organizar as informações;
converter os dados para JSON;
realizar requisições HTTP para a API.

Dessa maneira, o microcontrolador não precisa se comunicar diretamente com o servidor Web.

3. Servidor Web — Node.js

O servidor foi desenvolvido utilizando Node.js e Express.

A API recebe as informações enviadas pelo Gateway C# através de requisições HTTP utilizando JSON.

O servidor é responsável por:

receber os dados;
validar as informações recebidas;
encaminhar os valores para o classificador;
receber o resultado da Inteligência Artificial;
retornar a classificação;
disponibilizar informações para a interface Web.
4. Inteligência Artificial

A classificação das medições é realizada por um modelo de Machine Learning baseado em Árvore de Decisão (Decision Tree).

O classificador recebe a leitura processada e determina automaticamente a categoria correspondente.

O objetivo é transformar uma leitura numérica em uma informação mais simples de interpretar pelo usuário.

O modelo é executado através do arquivo:

ClassificadorArvore.py
5. Interface Web

A interface Web apresenta os dados recebidos de maneira visual e organizada.

Entre as informações apresentadas estão:

leitura atual;
valor de ADC;
valor convertido para CO₂;
classificação da qualidade do ar;
histórico das medições;
estado do filtro;
média das medições;
valor máximo;
valor mínimo;
horário da última atualização;
indicador visual do nível de CO₂.

A interface é atualizada conforme novas medições são processadas pelo sistema.

✨ Funcionalidades
Obrigatórias

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

Além dos requisitos principais, o sistema também conta com recursos adicionais de visualização e análise, como:

📊 estatísticas das medições;
📈 acompanhamento do histórico;
🔎 valores mínimo e máximo;
📉 cálculo de média;
🎚️ indicador visual do nível de CO₂;
🔘 indicação do estado do filtro.

Esses recursos ampliam a capacidade de acompanhamento dos dados pelo usuário.

🛠️ Tecnologias utilizadas
Tecnologia	Utilização
C	Programação do STM32
STM32F103C8	Aquisição das medições
STM32CubeIDE	Desenvolvimento e compilação do firmware
USB CDC	Comunicação serial com o computador
C#	Gateway de comunicação
Node.js	Servidor Web
Express	API REST
Python	Classificação utilizando IA
Scikit-learn	Modelo de Machine Learning
HTML	Estrutura da interface
CSS	Estilização
JavaScript	Funcionamento e atualização da interface
JSON	Formato de comunicação entre os módulos
HTTP	Comunicação entre Gateway e servidor
Git/GitHub	Controle de versão
📁 Estrutura do projeto

A estrutura principal do repositório está organizada da seguinte maneira:

MonitorAr_2K26/
│
├── ProjetoIntegrado_2K26/
│   │
│   ├── GatewayCSharp/
│   │   ├── ...
│   │
│   ├── Hardware/
│   │   └── Medicao/
│   │       ├── ...
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

Antes de executar o sistema, é necessário ter instalado:

STM32CubeIDE
.NET / Visual Studio para o Gateway C#
Node.js
Python 3
bibliotecas Python utilizadas pelo classificador
STM32F103C8 conectado ao computador
ambiente configurado para comunicação USB CDC
1. Clonar o repositório
git clone https://github.com/Tuany-rvlh/MonitorAr_2K26.git

Depois, entre na pasta:

cd MonitorAr_2K26
2. Instalar as dependências do servidor

Na raiz do projeto:

npm install

O projeto utiliza o Express como framework para o servidor Node.js.

3. Preparar o STM32

Abra o projeto do STM32 no STM32CubeIDE.

Verifique:

configuração do ADC;
configuração da USB;
comunicação USB CDC;
botão de ativação do filtro;
conexão do trimpot/potenciômetro;
compilação do firmware.

Após a compilação, grave o firmware no STM32.

4. Conectar o STM32

Conecte o STM32 ao computador através da USB.

Após a conexão, verifique qual Porta COM foi atribuída ao dispositivo.

Essa porta deverá ser utilizada pelo Gateway C#.

5. Iniciar o servidor

Execute:

node ProjetoIntegrado_2K26/servidor.js

O servidor ficará responsável por receber as requisições enviadas pelo Gateway.

6. Executar o Gateway C#

Abra o projeto localizado em:

ProjetoIntegrado_2K26/GatewayCSharp/

Configure a Porta COM correspondente ao STM32 e execute a aplicação.

O Gateway começará a:

Ler → Processar → Converter → Enviar

continuamente.

7. Acessar a interface

Com o servidor em execução, abra a interface Web pelo endereço disponibilizado pelo servidor.

A página exibirá os dados recebidos e os resultados da classificação.

🔄 Fluxo de uma medição

Uma medição percorre o sistema seguindo este fluxo:

1. Trimpot altera o sinal analógico
             ↓
2. STM32 realiza a leitura do ADC
             ↓
3. Filtro é aplicado, se estiver ativado
             ↓
4. STM32 envia a leitura via USB CDC
             ↓
5. Gateway C# recebe a informação
             ↓
6. Gateway organiza os dados
             ↓
7. Dados são convertidos para JSON
             ↓
8. Gateway envia uma requisição HTTP
             ↓
9. API Node.js recebe a medição
             ↓
10. Servidor chama o classificador
             ↓
11. Modelo de IA determina a categoria
             ↓
12. Resultado retorna para a aplicação
             ↓
13. Interface Web atualiza os dados
🔘 Filtro de média móvel

O sistema possui um filtro de média móvel, utilizado para reduzir oscilações nas medições.

Quando ativado, o sistema considera um conjunto de 10 amostras para calcular uma média.

De forma simplificada:

Média = (A1 + A2 + A3 + ... + A10) / 10

O filtro pode ser alternado através do botão conectado ao STM32.

Na interface Web, o usuário consegue visualizar se o filtro está ativado ou desativado.

🤖 Classificação por Inteligência Artificial

A classificação utiliza uma Árvore de Decisão, permitindo que o sistema associe automaticamente a leitura recebida a uma categoria.

O processo pode ser representado como:

Leitura
   ↓
Modelo de Machine Learning
   ↓
Classificação
   ↓
Interface Web

Essa abordagem permite transformar dados numéricos em uma informação mais intuitiva para o usuário.

📡 Comunicação entre os módulos

A comunicação do projeto utiliza diferentes tecnologias em cada etapa:

Origem	Destino	Comunicação
STM32	Gateway C#	USB CDC / Porta COM
Gateway C#	Node.js	HTTP
Gateway C#	Node.js	JSON
Node.js	Python	Execução do classificador
Node.js	Frontend	HTTP / dados Web

Essa divisão permite manter cada módulo responsável por uma função específica.

🧠 Decisões de implementação
Uso do STM32

O STM32 foi escolhido para representar a camada de aquisição de um sistema embarcado, realizando a leitura analógica e o pré-processamento dos dados.

Uso do C# como Gateway

O Gateway funciona como uma camada intermediária entre o hardware e a aplicação Web. Essa separação facilita o tratamento da comunicação serial e evita que o servidor precise acessar diretamente a Porta COM.

Uso de Node.js e Express

O Node.js foi utilizado para implementar o servidor e a API REST, centralizando o recebimento das medições e a comunicação com os demais componentes do sistema.

Uso de Python para IA

O Python foi utilizado na etapa de Inteligência Artificial devido à disponibilidade de bibliotecas voltadas para Machine Learning, sendo utilizada uma Árvore de Decisão para a classificação.

Uso de JSON

O JSON foi adotado como formato de troca de informações entre o Gateway e a API por ser simples, estruturado e adequado para comunicação entre aplicações diferentes.

🧪 Testes

O projeto também possui uma pasta destinada aos testes de comunicação pela Porta COM:

TestePortaCOM/

Ela contém recursos para simulação e testes da comunicação serial, permitindo testar partes do sistema mesmo sem utilizar diretamente o STM32.

🎥 Vídeo de apresentação

Vídeo de apresentação:
🔗 Adicionar aqui o link do vídeo no YouTube.

O vídeo deve apresentar o funcionamento completo do sistema, incluindo a aquisição da leitura, comunicação entre os módulos, classificação e visualização na interface Web.

📚 Projeto Integrado

Este projeto foi desenvolvido para integrar conhecimentos das seguintes disciplinas:

Sistemas Embarcados (SEB)
Linguagens de Programação (LPR)
Desenvolvimento de Aplicativos (DAPL)
Inteligência Artificial (IA)

A proposta envolve a construção de uma solução distribuída de aquisição, comunicação, processamento, classificação e visualização de dados, seguindo os requisitos definidos para o Projeto Integrado.

👥 Integrantes
Mariana Ferreira da Silva
Tuany Silva Pereira

📌 Status do projeto

🟢 Projeto concluído

O sistema possui integração entre:

Hardware + Comunicação Serial + Gateway C# + API REST + Inteligência Artificial + Interface Web

📄 Licença

Este projeto foi desenvolvido para fins educacionais, como parte das atividades do Projeto Integrado 2026.

🔗 Repositório

GitHub:
https://github.com/Tuany-rvlh/MonitorAr_2K26
