from src.transform.treatment import Treatment
from callmine.tgraph.static_graph import StaticGraph
from callmine.tgraph.temporal_graph import TemporalGraph
from callmine.tgraph.join_feature_files import JoinFeatures
from typing import Literal
from pathlib import Path
from config import Config
import pandas as pd



class FeatureEngineering:
    def __init__(self):
        self.features_path = Config.data_path / "configs" / "config_features.csv"
        self.wallet_path = Config.data_path / "data_selected_columns" / "wallets_features_classes_combined.parquet"

    def _run_static_graph(self, config_path: Path, output_path: Path):
        print("Running tgraph static_graph...")
        static_graph = StaticGraph(filename=config_path)
        static_graph.print_to_csv(output_path)
        static_graph.my_print()
        print(f"Static graph node vectors saved to: {output_path}")

        return static_graph.df_nodes

    def _run_temporal_graph(self, config_path: Path, output_path: Path, time_step_format:Literal['timestamp', 'number'] = 'number'):
        print("Running tgraph temporal_graph...")
        temporal_graph = TemporalGraph(filename=config_path, time_step_format=time_step_format)
        temporal_graph.print_to_csv(output_path)
        temporal_graph.my_print()
        print(f"Temporal graph node vectors saved to: {output_path}")

        return temporal_graph.df_nodes

    def _run_join_feature_files(self, static_graph_path: Path, temporal_graph_path: Path):
        print("Running tgraph join_features...")
        join_features = JoinFeatures(path_static=static_graph_path, path_temporal=temporal_graph_path)
        
        #join_features.print_to_csv(join_features_output_path)
        #print(f"Joined features saved to: {join_features_output_path}")

        return join_features.df_all #.to_csv(out_file_name, index=False)
    
    def _run_tgraph_features(self, config_path, static_graph_path, temporal_graph_path):
        self._run_static_graph(config_path, static_graph_path)
        self._run_temporal_graph(config_path, temporal_graph_path)
        return self._run_join_feature_files(static_graph_path, temporal_graph_path)

    def _tgraph_features(self):
        config_path = Config.data_path / "configs" / "config.csv"
        static_graph_path = Config.data_path / "configs" / "nodeVectors.csv"
        temporal_graph_path = Config.data_path / "configs" / "t_nodeVectors.csv"

        print("Creating first dataset...")
        print("Files:")
        print(config_path)
        print(static_graph_path)
        print(temporal_graph_path)
        print()
        return self._run_tgraph_features(config_path, static_graph_path, temporal_graph_path)
    
    def base_config(self):
        '''
        O base config vai ser as features do tgraph com wallet features
        '''
        df = self._tgraph_features()
        
        #pegar ultima wallet por timestep e definir as colunas
        wallets_features = pd.read_parquet(self.wallet_path).sort_values('time_step').groupby('address', as_index=False).last()
        wallets_features = wallets_features.rename(columns={"address":"node_ID"})

        df = df.merge(
            wallets_features,
            left_on="node_ID",
            right_on="node_ID",
            how="left"
        )

        #Sanity check:
        missing_wallets = (
            df["node_ID"]
            .loc[~df["node_ID"].isin(wallets_features["node_ID"])]
            .nunique()
        )
        if missing_wallets > 0:
            print(f"[ALERTA!!] Wallets sem feature: {missing_wallets}")
        #End sanity check

        df.to_csv(self.features_path, index=False)

    def generate_first_config(self):
        columns = [
            'node_ID',
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
            'out_median_measure',
            'class'
        ]
        df = pd.read_csv(self.features_path, usecols=columns)
        df = Treatment(df).remove_duplicates().remove_nulls().get_df()
        
        df.to_csv(Config.path_config_1, index=False)
        return self

    def generate_second_config(self):
        '''
         Mesmas features do dataset 1 só que com as duas métricas de IAT + call_count considerando os blocos
        - mapeamento:
            'in_median_iat' - blocks_btwn_input_txs_median
            'in_call_count', - num_txs_as receiver --> talvez trocar [TODO] validar com alguem
            'in_median_measure', - btc_received_median
            'out_median_iat', - blocks_btwn_output_txs_median
            'out_call_count', - num_txs_as_sender --> talvez trocar [TODO] validar com alguem
            'out_median_measure' - btc_sent_median
        
        - O in_degree é quantas wallets incidentes
        - O in_call_count é quantas transações que chegam --> isso que tenho pensado [TODO] validar com alguem
        '''
        columns = [
            'node_ID',
            'out_degree', 
            'in_degree',
            'core', 
            'weighted_out_degree',
            'weighted_in_degree', 
            "blocks_btwn_input_txs_median",
            "num_txs_as_receiver",
            "btc_received_median",
            "blocks_btwn_output_txs_median",
            "num_txs_as_sender",
            "btc_sent_median",
            'class'
        ]
        df = pd.read_csv(self.features_path, usecols=columns) # Config.data_path / "config_features_2.csv"

        columns_to_rename = {
            "blocks_btwn_input_txs_median": "in_median_iat",
            "num_txs_as_receiver": "in_call_count",
            "btc_received_median": "in_median_measure",
            "blocks_btwn_output_txs_median": "out_median_iat",
            "num_txs_as_sender": "out_call_count",
            "btc_sent_median": "out_median_measure"
        }
        df = df.rename(columns=columns_to_rename)
        df = Treatment(df).remove_duplicates().remove_nulls().get_df()
        df.to_csv(Config.path_config_2, index=False)
        return self
    
    def generate_third_config(self):
        '''
        Mesma que a primeira config só que removendo as linhas com classe unknown
        '''
        columns = [
            'node_ID',
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
            'out_median_measure',
            'class'
        ]
        df = pd.read_csv(self.features_path, usecols=columns)
        df = Treatment(df).remove_duplicates().remove_nulls().remove_unknown_class().get_df()
        
        df.to_csv(Config.path_config_3, index=False)
        return self

    def generate_fourth_config(self):
        """
        Mesma que a segunda config só que removendo as linhas com classe unknown
        """
        columns = [
            'node_ID',
            'out_degree', 
            'in_degree',
            'core', 
            'weighted_out_degree',
            'weighted_in_degree', 
            "blocks_btwn_input_txs_median",
            "num_txs_as_receiver",
            "btc_received_median",
            "blocks_btwn_output_txs_median",
            "num_txs_as_sender",
            "btc_sent_median",
            'class'
        ]
        df = pd.read_csv(self.features_path, usecols=columns)

        columns_to_rename = {
            "blocks_btwn_input_txs_median": "in_median_iat",
            "num_txs_as_receiver": "in_call_count",
            "btc_received_median": "in_median_measure",
            "blocks_btwn_output_txs_median": "out_median_iat",
            "num_txs_as_sender": "out_call_count",
            "btc_sent_median": "out_median_measure"
        }
        df = df.rename(columns=columns_to_rename)
        df = Treatment(df).remove_duplicates().remove_nulls().remove_unknown_class().get_df()
        df.to_csv(Config.path_config_4, index=False)
        return self
