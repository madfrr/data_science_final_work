import pandas as pd
import os
from config import Config

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

    def create_config(self, dataframes, with_fees=False):
        '''
        [TODO] Esse cara aqui preciso excluir fees do measurement
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
        addr_addr_tx.to_csv(self.data_path / self.output_dir / "raw_config.csv", index=False)
        return self
    
    def run(self):
        dataframes = self.read_parquets()
        self.create_config(dataframes)


from callmine.tgraph.static_graph import StaticGraph
from callmine.tgraph.temporal_graph import TemporalGraph
from callmine.tgraph.join_feature_files import JoinFeatures
from typing import Literal
from pathlib import Path

class FeatureEngineering:
    def __init__(self):
        pass

    def create_base_config(self):
        CreateConfigs(data_path=Config.data_path, input_dir="data_selected_columns", output_dir="configs").run()

    def run_static_graph(self, config_path: Path, output_path: Path):
        print("Running tgraph static_graph...")
        static_graph = StaticGraph(filename=config_path)
        static_graph.print_to_csv(output_path)
        static_graph.my_print()
        print(f"Static graph node vectors saved to: {output_path}")

        return static_graph.df_nodes

    def run_temporal_graph(self, config_path: Path, output_path: Path, time_step_format:Literal['timestamp', 'number'] = 'number'):
        print("Running tgraph temporal_graph...")
        temporal_graph = TemporalGraph(filename=config_path, time_step_format=time_step_format)
        temporal_graph.print_to_csv(output_path)
        temporal_graph.my_print()
        print(f"Temporal graph node vectors saved to: {output_path}")

        return temporal_graph.df_nodes

    def run_join_feature_files(self, static_graph_path: Path, temporal_graph_path: Path, join_features_output_path: Path):
        print("Running tgraph join_features...")
        join_features = JoinFeatures(path_static=static_graph_path, path_temporal=temporal_graph_path)
        join_features.print_to_csv(join_features_output_path)
        print(f"Joined features saved to: {join_features_output_path}")

        return join_features.df_all
    
    def run_tgraph_features(self, config_path, static_graph_path, temporal_graph_path, join_features_output_path):
        self.run_static_graph(config_path, static_graph_path)
        self.run_temporal_graph(config_path, temporal_graph_path)
        self.run_join_feature_files(static_graph_path, temporal_graph_path, join_features_output_path)

    def create_first_dataset(self):
        '''
        keys = [
            'out_degree', 
            'in_degree',
            'core', 
            'weighted_out_degree',
            'weighted_in_degree', 
            'in_median_iat',
            'in_call_count', 
            'in_median_measure',
            'out_median_iat', 
            'out_call_count',
            'out_median_measure'
        ]
        call_count é o group.size onde o grupo é agrupamento do node direction com timestamp??
        como se fosse qtd de valores que tem no grupo
        '''
        config_path = Config.data_path / "configs" / "config.csv"
        static_graph_path = Config.data_path / "nodeVectors.csv"
        temporal_graph_path = Config.data_path / "t_nodeVectors.csv"
        join_features_output_path = Config.data_path / "config_features_1.csv"

        print("Creating first dataset...")
        print("Files:")
        print(config_path)
        print(static_graph_path)
        print(temporal_graph_path)
        print(join_features_output_path)
        print()
        self.run_tgraph_features(config_path, static_graph_path, temporal_graph_path, join_features_output_path)
        print(f"Files created for first dataset!! Check {join_features_output_path}")
    
    def create_second_dataset(self):
        '''
        Mesmas features do dataset 1 só que com as duas métricas de IAT + call_count considerando os blocos
        Como fazer:
        - criar a msm config que a anterior
        - rodar o static_graph --> pegar todas as métricas de static graph
        - Fazer mapeamento:
            'in_median_iat' - blocks_btwn_input_txs_median
            'in_call_count', - num_txs_as receiver --> talvez trocar [TODO] validar com alguem
            'in_median_measure', - btc_received_median
            'out_median_iat', - blocks_btwn_output_txs_median
            'out_call_count', - num_txs_as_sender --> talvez trocar [TODO] validar com alguem
            'out_median_measure' - btc_sent_median
        
        - O in_degree é quantas wallets incidentes
        - O in_call_count é quantas transações que chegam --> isso que tenho pensado [TODO] validar com alguem
        '''
        config_path = Config.data_path / "configs" / "config.csv"
        static_graph_path = Config.data_path / "nodeVectors2.csv"
        static_graph_df = self.run_static_graph(config_path, static_graph_path)

        FEATURE_MAPPING = {
            "in_median_iat": "blocks_btwn_input_txs_median",
            "in_call_count": "num_txs_as_receiver",
            "in_median_measure": "btc_received_median",
            "out_median_iat": "blocks_btwn_output_txs_median",
            "out_call_count": "num_txs_as_sender",
            "out_median_measure": "btc_sent_median",
        }
        wallets_columns = ["address"] + list(FEATURE_MAPPING.values())
        
        wallet_path = Config.data_path / "data_selected_columns" / "wallets_features.parquet"
        #pegar ultima wallet por timestep e definir as colunas
        wallets_features = pd.read_parquet(wallet_path).sort_values('time_step').groupby('address', as_index=False).last()
        wallets_features = wallets_features[wallets_columns].rename(columns={"address":"node_ID"})

        static_graph_df = static_graph_df.merge(
            wallets_features,
            left_on="node_ID",
            right_on="node_ID",
            how="left"
        )

        static_graph_df = static_graph_df.rename(
            columns={v: k for k, v in FEATURE_MAPPING.items()}
        )

        #Sanity check:
        missing_wallets = (
            static_graph_df["node_ID"]
            .loc[~static_graph_df["node_ID"].isin(wallets_features["node_ID"])]
            .nunique()
        )
        if missing_wallets > 0:
            print(f"[ALERTA!!] Wallets sem feature: {missing_wallets}")
        #End sanity check

        static_graph_df.to_csv(Config.data_path / "config_features_2.csv", index=False) 
        return static_graph_df # [TODO] conferir se esse csv ta certinho

    def create_third_dataset():
        '''
        Repassar com o Robson pra entender quais são as features que ele usou no fraudguess ou que acha que seria interessante
        Fazer isso segunda-feira depois que as análises já estiverem prontas
        '''
        pass