import pandas as pd
import os

class CreateConfigs:
    def __init__(self, data_path, input_dir, output_dir):
        self.data_path = data_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(data_path / output_dir, exist_ok=True)
        self.configs = {}

    def read_parquet(self, file_name:str):
        file_path = self.data_path / self.input_dir / f"{file_name}.parquet"
        return pd.read_parquet(file_path)

    def create_config(self, with_fees=False):
        '''
        input_address, outut_address, measure=total_btc + fees, time_step
        '''
        addr_tx = self.read_parquet("AddrTx_edgelist")
        tx_addr = self.read_parquet("TxAddr_edgelist")
        tx_features = self.read_parquet("txs_features")
        tx_classes = self.read_parquet("txs_classes")

        addr_addr_tx = addr_tx.merge(tx_addr, on="tx_id", how="inner")

        if with_fees:
            addr_addr_tx = addr_addr_tx.merge(tx_features[['tx_id', 'time_step', 'total_btc', 'fees']], on="tx_id", how="inner")
            addr_addr_tx['measure'] = addr_addr_tx['total_btc'] + addr_addr_tx['fees']
        else:
            addr_addr_tx = addr_addr_tx.merge(tx_features[['tx_id', 'time_step', 'total_btc']], on="tx_id", how="inner")
            addr_addr_tx['measure'] = addr_addr_tx['total_btc']

        addr_addr_tx = addr_addr_tx.merge(tx_classes, on="tx_id", how="left", suffixes=('', '_class'))
        print(addr_addr_tx.head())

        config = addr_addr_tx[['input_address', 'output_address', 'measure', 'time_step']]
        config = config.rename(columns={
            'input_address': 'source',
            'output_address': 'destination',
            'time_step': 'timestamp'
        })
        config.to_csv(self.data_path / self.output_dir / "config.csv", index=False)
        return self
    
    def run(self):
        self.create_config()