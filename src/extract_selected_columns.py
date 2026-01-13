from pathlib import Path
import pandas as pd
import os

class SelectColumns():
    def __init__(self, data_path, input_dir = "raw", output_dir="data_selected_columns"):
        self.output_path = data_path / output_dir
        self.input_path = data_path / input_dir
        os.makedirs(self.output_path, exist_ok=True)

        self.file_columns_mapping = {
            "wallets_features.csv": [
                "address",
                "Time step",
                "num_txs_as_sender",
                "num_txs_as receiver",
                "total_txs",
                "btc_transacted_total",
                "btc_sent_total",
                "btc_received_total",
                "fees_total",
                "fees_as_share_total",
                "btc_sent_median",
			    "btc_received_median",
                "blocks_btwn_input_txs_median", #in_median_iat
			    "blocks_btwn_output_txs_median" #out_median_iat
            ],
            "wallets_classes.csv": [
                "address",
                "class"
            ],
            "wallets_features_classes_combined.csv": [
                "address",
                "class",
                "Time step",
                "num_txs_as_sender",
                "num_txs_as receiver",
                "total_txs",
                "btc_transacted_total",
                "btc_sent_total",
                "btc_received_total",
                "fees_total",
                "fees_as_share_total",
                "btc_sent_median",
			    "btc_received_median",
                "blocks_btwn_input_txs_median",
			    "blocks_btwn_output_txs_median"
            ],
            "AddrAddr_edgelist.csv": ["input_address", "output_address"],
            "AddrTx_edgelist.csv": ["input_address", "txId"],
            "TxAddr_edgelist.csv": ["txId", "output_address"],
            "txs_classes.csv": ["txId", "class"],
            "txs_edgelist.csv": ["txId1", "txId2"],
            "txs_features.csv": [
                "txId", 
                "Time step", 
                "in_txs_degree", 
                "out_txs_degree", 
                "total_BTC", 
                "fees", 
                "size", 
            ]
        }

    def check_if_folder_already_exists(self):
        if not os.path.exists(self.input_path) or not os.listdir(self.input_path):
            raise FileNotFoundError(f"\n✗ Folder '{self.input_path}' does not exist or is empty. Please run the extraction step first.")
        if os.path.exists(self.output_path) and os.listdir(self.output_path):
            print(f"\n✓ Folder '{self.output_path}' already exists and is not empty. Skipping download.")
            return True
        return False
    
    def rename_columns(self, df):
        #[TODO] Repassar isso para alguma etapa de transformação
        columns_to_rename = {
            "Time step": "time_step",
            "txId": "tx_id",
            "txId1": "tx_id_1",
            "txId2": "tx_id_2",
            "total_BTC": "total_btc",
            "num_txs_as receiver": "num_txs_as_receiver"
        }
        return df.rename(columns=columns_to_rename)

    def format_columns(self):
        for file, columns in self.file_columns_mapping.items():
            df = pd.read_csv(self.input_path / file, usecols=columns)
            df = self.rename_columns(df)
            output_file = file.replace(".csv", ".parquet")
            df.to_parquet(self.output_path / output_file, index=False)
            print(f"✓ Processed and saved: {file} with columns: {list(df.columns)}")

    def run(self):
        if self.check_if_folder_already_exists():
            return
        self.format_columns()
                     
