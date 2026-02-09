# Data Dictionary — Elliptic++ Dataset

## wallets_features.csv

### Identificação e Tempo
* **address**
  Identificador único da wallet (endereço Bitcoin).
* **Time step**
  Janela temporal discreta na qual as features foram calculadas.

### Atividade Transacional
* **num_txs_as_sender**
  Número de transações em que a wallet atuou como remetente.
* **num_txs_as_receiver**
  Número de transações em que a wallet atuou como destinatário.
* **total_txs**
  Total de transações associadas à wallet no timestep.
* **num_timesteps_appeared_in**
  Número de janelas temporais distintas em que a wallet aparece.

### Temporalidade em Blocos
* **first_block_appeared_in**
  Altura do bloco em que a wallet aparece pela primeira vez.
* **last_block_appeared_in**
  Altura do bloco da última aparição da wallet.
* **lifetime_in_blocks**
  Diferença entre o primeiro e o último bloco associado à wallet.
* **first_sent_block**
  Bloco da primeira transação enviada pela wallet.
* **first_received_block**
  Bloco da primeira transação recebida pela wallet.

### Volume Total de BTC
* **btc_transacted_total**
  Quantidade total de BTC transacionada pela wallet.
* **btc_transacted_min**
  Menor valor de BTC em uma transação associada à wallet.
* **btc_transacted_max**
  Maior valor de BTC em uma transação associada à wallet.
* **btc_transacted_mean**
  Valor médio de BTC por transação.
* **btc_transacted_median**
  Valor mediano de BTC por transação.

### BTC Enviado
* **btc_sent_total**
  Total de BTC enviado pela wallet.
* **btc_sent_min**
  Menor valor de BTC enviado em uma transação.
* **btc_sent_max**
  Maior valor de BTC enviado em uma transação.
* **btc_sent_mean**
  Valor médio de BTC enviado por transação.
* **btc_sent_median**
  Valor mediano de BTC enviado por transação.

### BTC Recebido
* **btc_received_total**
  Total de BTC recebido pela wallet.
* **btc_received_min**
  Menor valor de BTC recebido em uma transação.
* **btc_received_max**
  Maior valor de BTC recebido em uma transação.
* **btc_received_mean**
  Valor médio de BTC recebido por transação.
* **btc_received_median**
  Valor mediano de BTC recebido por transação.

### Fees Absolutas
* **fees_total**
  Soma total das taxas pagas pela wallet.
* **fees_min**
  Menor taxa paga em uma transação.
* **fees_max**
  Maior taxa paga em uma transação.
* **fees_mean**
  Taxa média paga por transação.
* **fees_median**
  Taxa mediana paga por transação.

### Fees Relativas ao Valor
* **fees_as_share_total**
  Soma das taxas como proporção do valor das transações.
* **fees_as_share_min**
  Menor proporção fee/valor observada.
* **fees_as_share_max**
  Maior proporção fee/valor observada.
* **fees_as_share_mean**
  Proporção média fee/valor.
* **fees_as_share_median**
  Proporção mediana fee/valor.

### Intervalos Temporais Entre Transações
* **blocks_btwn_txs_total**
  Soma dos intervalos em blocos entre transações consecutivas.
* **blocks_btwn_txs_min**
  Menor intervalo em blocos entre transações.
* **blocks_btwn_txs_max**
  Maior intervalo em blocos entre transações.
* **blocks_btwn_txs_mean**
  Intervalo médio em blocos entre transações.
* **blocks_btwn_txs_median**
  Intervalo mediano em blocos entre transações.

### Intervalos Entre Inputs
* **blocks_btwn_input_txs_total**
  Soma dos intervalos entre transações de entrada.
* **blocks_btwn_input_txs_min**
  Menor intervalo entre transações de entrada.
* **blocks_btwn_input_txs_max**
  Maior intervalo entre transações de entrada.
* **blocks_btwn_input_txs_mean**
  Intervalo médio entre transações de entrada.
* **blocks_btwn_input_txs_median**
  Intervalo mediano entre transações de entrada.

### Intervalos Entre Outputs
* **blocks_btwn_output_txs_total**
  Soma dos intervalos entre transações de saída.
* **blocks_btwn_output_txs_min**
  Menor intervalo entre transações de saída.
* **blocks_btwn_output_txs_max**
  Maior intervalo entre transações de saída.
* **blocks_btwn_output_txs_mean**
  Intervalo médio entre transações de saída.
* **blocks_btwn_output_txs_median**
  Intervalo mediano entre transações de saída.

### Interação com Outras Wallets
* **num_addr_transacted_multiple**
  Número de endereços distintos com os quais houve múltiplas transações.
* **transacted_w_address_total**
  Total de endereços distintos transacionados.
* **transacted_w_address_min**
  Menor número de interações com um mesmo endereço.
* **transacted_w_address_max**
  Maior número de interações com um mesmo endereço.
* **transacted_w_address_mean**
  Média de interações por endereço distinto.
* **transacted_w_address_median**
  Mediana de interações por endereço distinto.

---

## wallets_classes.csv
* **address**
  Identificador da wallet.
* **class**
  Rótulo da wallet (1 = ilícita, 2 = lícita, 3 = desconhecida).

---

## wallets_features_classes_combined.csv
Contém todas as variáveis de `wallets_features.csv` acrescidas de:

* **class**
  Rótulo supervisionado da wallet.

---

## txs_features.csv

### Identificação e Tempo
* **txId**
  Identificador único da transação.
* **Time step**
  Janela temporal discreta da transação.

### Conectividade Transacional
* **in_txs_degree**
  Número de transações predecessoras conectadas.
* **out_txs_degree**
  Número de transações sucessoras conectadas.

### Valor, Taxas e Estrutura
* **total_BTC**
  Quantidade total de BTC movimentada na transação.
* **fees**
  Taxa paga pela transação.
* **size**
  Tamanho da transação em bytes.

### Endereços de Entrada
* **num_input_addresses**
  Número de endereços de entrada.
* **in_BTC_min**
  Menor valor de BTC entre os inputs.
* **in_BTC_max**
  Maior valor de BTC entre os inputs.
* **in_BTC_mean**
  Valor médio de BTC nos inputs.
* **in_BTC_median**
  Valor mediano de BTC nos inputs.
* **in_BTC_total**
  Soma total de BTC nos inputs.

### Endereços de Saída
* **num_output_addresses**
  Número de endereços de saída.
* **out_BTC_min**
  Menor valor de BTC entre os outputs.
* **out_BTC_max**
  Maior valor de BTC entre os outputs.
* **out_BTC_mean**
  Valor médio de BTC nos outputs.
* **out_BTC_median**
  Valor mediano de BTC nos outputs.
* **out_BTC_total**
  Soma total de BTC nos outputs.

---

## txs_classes.csv
* **txId**
  Identificador da transação.
* **class**
  Rótulo da transação (1 = ilícita, 2 = lícita, 3 = desconhecida).

---

## AddrAddr_edgelist.csv
* **input_address**
  Wallet de origem.
* **output_address**
  Wallet de destino.

---

## AddrTx_edgelist.csv
* **input_address**
  Wallet de entrada.
* **txId**
  Transação associada.

---

## TxAddr_edgelist.csv
* **txId**
  Transação.
* **output_address**
  Wallet de saída.

---

## txs_edgelist.csv
* **txId1**
  Transação predecessora.
* **txId2**
  Transação sucessora.
