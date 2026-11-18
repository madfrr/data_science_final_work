# data_science_final_work
referencias:
https://github.com/git-disl/EllipticPlusPlus
https://drive.google.com/drive/folders/1MRPXz79Lu_JGLlJ21MDfML44dKN9R08l?usp=sharing

callmine
tgraph
https://github.com/mtcazzolato/tgraph-spot
https://github.com/mtcazzolato/tgrapp
https://github.com/mtcazzolato/callmine

Tem uma aplicação no mercado financeiro:
FraudGuess: Spotting and explaining new types of fraud in million-scale financial data
- Formato de dados: card ID, merchant ID, amount, timestamp

Posso tentar adaptar para o meu caso onde eu tenho endereço de origem, endereço de destino, ai posso pegar qlquer característica da transaction (nro de blocos, valor...) e o time step (que tbm posso modelar com o nro de blocos)


Pesquisar:

🔹 CallMine

Park et al., CallMine: A Visual Graph Mining System for Detecting Phone Call Fraud, CIKM 2023.
Por quê: mineração visual, padrões estruturais.

🔹 FRAUDGUESS

Cordeiro et al., FRAUDGUESS: Spotting and Explaining New Types of Fraud in Million-Scale Financial Data, 2025.
Por quê: padrões repetitivos + explicação.

🔹 Elliptic / Elliptic++

Weber et al., Anti-Money Laundering in Bitcoin, KDD 2019.
Por quê: dataset e rótulos.

🔹 Ranking-based evaluation

Akoglu et al., Anomaly Detection in Large Graphs, DMKD 2015.
Por quê: avaliação sem probabilidade.


## Snippets
conda activate myenv

git -c commit.gpgsign=false commit -m 'resultados_compilados'

main
ExtractFromDrive
SelectColumns
Validations
-- Tratamento de dados
-- análise exploratória tem que ser aqui

CreateConfigs -> AGREGAR COM RUN_CALL_MINE PARA GERAR DATASET DE FEATURE
run_call_mine -> AGREGAR COM CREATECONFIGS PRA GERAR DATASET DE FEATURE

run_gen2out
-- run_outros modelos/algoritmos de anomalia
Metrics

config.py
env

CRISP:
1. Entendimento do Negócio (Definição do Problema);
2. Entendimento dos Dados;  ← análise exploratória
3. Preparação dos Dados;  ← data cleasing
4. Treinamento (Modelagem);
5. Avaliação;
6. Deployment.

Testar com:
Python 3.10.19
Python 3.14.3

TODO:
- Preciso subir a versão do python desse projeto para 3.14, para conseguir usar as novas libs.
    - Como não tenho teste unitário e teste de integração, talvez vale eu olhar o callmine e o tgraph pra ver se já tem exemplos dummy, rodar 

- Preciso decidir se vou querer ou não editar o callmine, gen2out, lookout, tgraph....

A ideia é:
1. Ou fazer uma seleção automática de atributos, sendo que essa seleção pode ser variável. Dai vai acabar sendo uma framework de explainable AI.
2. Ou pensar em formas/novas heurísticas para alterar o gen2out e deixar ele focado em um escopo diferente

Eu prefiro a primeira ideia! Como eu devo fazer isso:
- Primeiro eu posso fazer uma poc:
    - Tentar rodar dnovo o meu algoritmo, gerando as métricas do TCC. Pegar a config do tcc com maior valor
    - Pegar 2~3 algoritmos supervisionados, gerar o shap_values (parametrizado para printar o gráfico ou não). Fazer isso com uma versão mais atualizada do python.
    - Com o shap_values, escolher as features que se sairam melhor. Pode ser manualmente. Fazer algumas permutações legais;
    - Rodar dnovo o meu algoritmo, só que marretando as novas features. Dependendo do qto melhorar, vale eu aumentar a versão do python, atualizar o call_mine para a nova versão, e fazer tudo de forma automatica --> O usuário seleciona o algoritmo, marretando os parametros, gerar as features automaticamente e isso ser inputado tbm de forma automatica


Débitos técnicos:
- Revisar o arquivo de config.py