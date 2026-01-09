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


 TODO:
 - ler artigos:
    - elliptic ++ --> Continuar depois
    - FraudGuess: Spotting and explaining new types of fraud in million-scale financial data
- [Done] baixar datasets

- Fazer um summario com todos os dados, para entender as tabelas
- Fazer os pipeline de dados para conseguir pegar um percentual dos dados com base 
- Subir os datasets no google drive e dar o gitignore

- Criar uma etapa de transformação de dados para criar (endereço, endereço, medida e timestep)
- usar o call-mine da cazzolato
- Entender os resultados
----> Até domingo. Depois decidir o que falta fazer. Se eu ter algum resultado, ou conseguir reaproveitar os dados da mineração pra aplicar algum algoritmo de machine learning, já da pra fazer o TCC em cima

- verificar pontos onde podem ter algum problema
- no ruim, ler o cs224

Pesquisar:

Google Scholar: "CallMine" Elliptic / "CallMine" bitcoin / "CallMine" blockchain
GitHub code search: callmine elliptic / callmine bitcoin / callmine aml
ArXiv full-text: CallMine + transaction graph

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

git -c commit.gpgsign=false commit -m 'nome commit'
