import pandas as pd
import os

file_names = [
        "wallets_features",
        "wallets_classes",
        "wallets_features_classes_combined",
        "AddrAddr_edgelist",
        "AddrTx_edgelist",
        "TxAddr_edgelist",
        "txs_classes",
        "txs_edgelist",
        "txs_features"
    ]

class CreateConfigs:
    def __init__(self, data_path, input_dir, output_dir):
        self.data_path = data_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.file_names = file_names
        os.makedirs(data_path / output_dir, exist_ok=True)
        self.configs = {}

    def read_parquets(self):
        dataframes = {}
        for file_name in self.file_names:
            file_path = self.data_path / self.input_dir / f"{file_name}.parquet"
            df = pd.read_parquet(file_path)
            dataframes[file_name] = df
        return dataframes

    def create_config_1(self, dataframes):
        '''
        AddrTx_edgelist (input_address, tx_id)
        TxAddr_edgelist (output_address, tx_id)
        tx_features (tx_id, time_step)
        txs_classes
        merge to create a dataset with:
        (input_address, output_address, tx_id, time_step, measurement=1)
        - validar se para cada linha, os timesteps são iguais
        - merge 2x com dataset txs_classes para pegar a classe de cada transação
        - classe vai ser 1 se qualquer uma das transações for ilicita
        - caso contrario, 2 se qlquer uma for licitia
        - caso contrario, 3 - unknown
        df final com colunas
        (source, target, measurement, timestamp, class)
        - exportar como config_1.parquet
        input_address, outut_address, 1, time_step
        '''
        addr_tx = dataframes["AddrTx_edgelist"]
        tx_addr = dataframes["TxAddr_edgelist"]
        tx_features = dataframes["txs_features"]
        tx_classes = dataframes["txs_classes"]
        
        addr_addr_tx = addr_tx.merge(tx_addr, on="tx_id", how="inner")
        addr_addr_tx = addr_addr_tx.merge(tx_features[['tx_id', 'time_step']], on="tx_id", how="inner")
        addr_addr_tx['measure'] = 1
        addr_addr_tx = addr_addr_tx.merge(tx_classes, on="tx_id", how="left", suffixes=('', '_class'))
        print(addr_addr_tx.head())

        config = addr_addr_tx[['input_address', 'output_address', 'measure', 'time_step']]
        config = config.rename(columns={
            'input_address': 'source',
            'output_address': 'destination',
            'time_step': 'timestamp'
        })
        config.to_csv(self.data_path / self.output_dir / "config_1.csv", index=False)
        addr_addr_tx.to_csv(self.data_path / self.output_dir / "raw_config_1.csv", index=False)
        return self

    def create_config_2(self, dataframes):
        '''
        Reaproveitar a estrutura da primeira config
        pegar total_bdc + fees da txs_features da tx_id_input
        Posso fazer variantes total bdc, fees, total_bdc + fees
        input_address, outut_address, measure=total_btc + fees, time_step
        '''
        addr_tx = dataframes["AddrTx_edgelist"]
        tx_addr = dataframes["TxAddr_edgelist"]
        tx_features = dataframes["txs_features"]
        tx_classes = dataframes["txs_classes"]
        
        addr_addr_tx = addr_tx.merge(tx_addr, on="tx_id", how="inner")
        addr_addr_tx = addr_addr_tx.merge(tx_features[['tx_id', 'time_step', 'total_btc', 'fees']], on="tx_id", how="inner")
        addr_addr_tx['measure'] = addr_addr_tx['total_btc'] + addr_addr_tx['fees']
        addr_addr_tx = addr_addr_tx.merge(tx_classes, on="tx_id", how="left", suffixes=('', '_class'))
        print(addr_addr_tx.head())

        config = addr_addr_tx[['input_address', 'output_address', 'measure', 'time_step']]
        config = config.rename(columns={
            'input_address': 'source',
            'output_address': 'destination',
            'time_step': 'timestamp'
        })
        config.to_csv(self.data_path / self.output_dir / "config_2.csv", index=False)
        addr_addr_tx.to_csv(self.data_path / self.output_dir / "raw_config_2.csv", index=False)
        return self

    def create_config_3(self, dataframes):
        '''
        txs_edgelist (tx_id_1, tx_id_2)
        tx_features (tx_id, time_step)
        txs_classes (tx_id, class)
        merge to create a dataset with:
        (tx_id_input, tx_id_output, time_step_input, time_step_output, measurement=total_btc + fees)
        - merge 2x com dataset txs_classes para pegar a classe de cada transação
        - classe vai ser 1 se qualquer uma das transações for ilicita
        - caso contrario, 2 se qlquer uma for licitia
        - caso contrario, 3 - unknown
        df final com colunas
        (source, target, measurement, timestamp, class)
        - exportar como config_1.parquet
        '''
        tx_features = dataframes["txs_features"]
        tx_classes = dataframes["txs_classes"]
        txs_edgelist = dataframes["txs_edgelist"]

        txs_merged = txs_edgelist.merge(
            tx_features[['tx_id', 'time_step', 'total_btc', 'fees']],
            left_on='tx_id_1',
            right_on='tx_id',
            how='inner'
        ).rename(columns={
            'time_step': 'time_step_input',
            'total_btc': 'total_btc_input',
            'fees': 'fees_input',
            'tx_id_1': 'tx_id_input'
        }).drop(columns=['tx_id'])

        txs_merged = txs_merged.merge(
            tx_features[['tx_id', 'time_step', 'total_btc', 'fees']],
            left_on='tx_id_2',
            right_on='tx_id',
            how='inner'
        ).rename(columns={
            'time_step': 'time_step_output',
            'total_btc': 'total_btc_output',
            'fees': 'fees_output',
            'tx_id_2': 'tx_id_output'
        }).drop(columns=['tx_id'])
        
        # acho que posso usar o time_step_input como timestamp

        # também vou usar measurement = 1
        # mas posso usar isso: https://chatgpt.com/share/6948ad8d-ea54-8004-b976-a7c12ed2bce1
        # Svalue​(i,j)=
        # max(out_BTC_total_i,in_BTC_total_j) /
        # min(out_BTC_total_i,in_BTC_total_j)
        return self
    
    def run(self):
        dataframes = self.read_parquets()
        self.create_config_1(dataframes)
        self.create_config_2(dataframes)
        #self.create_config_3(dataframes)