from src.extract import ExtractFromDrive
from src.selected_columns import SelectColumns
from src.validations import Validations
from src.create_configs import CreateConfigs
from src.metrics import Metrics
from callmine.tgraph.static_graph import StaticGraph
from callmine.tgraph.temporal_graph import TemporalGraph
from callmine.tgraph.join_feature_files import JoinFeatures
from callmine.callmine_focus.run_callmine_focus import call_mine_main, runGen2Out
#from callmine.callmine_focus.gen2Out.gen2out import gen2Out
import numpy as np
from pathlib import Path
import pandas as pd

file_names = [
        "wallets_features.csv",
        "wallets_classes.csv",
        "wallets_features_classes_combined.csv",
        "AddrAddr_edgelist.csv",
        "AddrTx_edgelist.csv",
        "TxAddr_edgelist.csv",
        "txs_classes.csv",
        "txs_edgelist.csv",
        "txs_features.csv"
    ]
data_path = Path(__file__).parent / "data"

CLASSE_ILICITA = 1
CLASSE_LICITA = 2
CLASSE_UNKNOWN = 3


def print_data_types():
    print("\n✓ Extracted files:")
    
    for file in file_names:
        print(f"- {file}")
        file_path = data_path / file
        if not file_path.exists():
            print(f"  ✗ Warning: {file} not found in {data_path}")
            continue

        print(f"  ✓ Data types:")
        df = pd.read_csv(file_path)
        for col in df.columns:
            print(f"{col}: {df[col].dtype}")

        print("-" * 40)
        print()

def run_static_graph(main_config_file_path: Path):
    static_graph = StaticGraph(filename=main_config_file_path)
    static_graph_output_path = data_path / "nodeVectors.csv"
    static_graph.print_to_csv(static_graph_output_path)
    static_graph.my_print()
    print(f"Static graph node vectors saved to: {static_graph_output_path}")

    return static_graph.df_nodes

def run_temporal_graph(main_config_file_path: Path):
    temporal_graph = TemporalGraph(filename=main_config_file_path)
    temporal_graph_output_path = data_path / "t_nodeVectors.csv"
    temporal_graph.print_to_csv(temporal_graph_output_path)
    temporal_graph.my_print()
    print(f"Temporal graph node vectors saved to: {temporal_graph_output_path}")

    return temporal_graph.df_nodes

def run_join_feature_files():
    temporal_graph_path = data_path / "t_nodeVectors.csv"
    static_graph_path = data_path / "nodeVectors.csv"
    join_features_output_path = data_path / "allFeatures_nodeVectors.csv"

    join_features = JoinFeatures(path_temporal=temporal_graph_path, path_static=static_graph_path)
    join_features.print_to_csv(join_features_output_path)
    print(f"Joined features saved to: {join_features_output_path}")

    return join_features.df_all

def run_callmine_focus(setup):
    '''
    setup must be 1 or 2
    '''
    setup_map = {
        1: {
            'path_features' : data_path / "allFeatures_nodeVectors.csv",
            'detection_option' : 1,
            'num_outliers' : 10,
            'budget' : 5,
            'dimensionality' : 2,
            'output_path' : str(Path(__file__).parent.parent / 'callmine' / 'outputs')
        },
        2: {
            'path_features' : data_path / "allFeatures_nodeVectors.csv",
            'detection_option' : 1,
            'num_outliers' : 10,
            'budget' : 5,
            'dimensionality' : 3,
            'output_path' : str(Path(__file__).parent.parent / 'callmine' / 'outputs')
        }
    }
    print(*setup_map[setup].values())
    call_mine_main(('dummy', *setup_map[setup].values()))

def sorted_gen2out_scores(read_if_cached=False, is_to_save=False):
    '''
    Posso transformar isso daqui em uma classe para testar diferentes chaves em diferentes algoritmos de detecção de anomalia
    '''
    scores_path = data_path / "gen2out_scores_sorted.csv"
    if scores_path.exists() and read_if_cached:
        print(f"Reading cached Gen2Out scores from: {scores_path}")
        df_scores = pd.read_csv(scores_path)
        return list(zip(df_scores['node_ID'], df_scores['anomaly_score']))


    df_features = pd.read_csv(data_path / "allFeatures_nodeVectors.csv")
    keys = ['out_degree', 'in_degree',
        'core', 'weighted_out_degree',
        'weighted_in_degree', 'in_median_iat',
        'in_call_count', 'in_median_measure',
        'out_median_iat', 'out_call_count',
        'out_median_measure']
    scores = runGen2Out(ids = df_features['node_ID'],
                            features = np.asarray(df_features[keys], dtype = float),
                            option=1)
    #scores = sorted(scores, key=lambda x: x[1], reverse=False)
    scores = [(node_id, 1- score) for node_id, score in scores] #invertendo valores de score

    if is_to_save:
        df_scores = pd.DataFrame(scores, columns=["node_ID", "anomaly_score"])
        df_scores.to_csv(scores_path, index=False)
        print(f"Gen2Out sorted scores saved to: {scores_path}")

    return scores

def get_address_class_lookup():
    path = data_path / 'data_selected_columns' / "wallets_classes.parquet"
    df = pd.read_parquet(path, columns=["address", "class"])
    return dict(zip(df["address"], df["class"]))

def main():
    #ExtractFromDrive(data_path=data_path).run()
    print()
    print("="*100)
    print()
    # print_data_types()
    #SelectColumns(data_path=data_path).run()
    print()
    print("="*100)
    print()
    #Validations(data_path=data_path, skip=True).run()
    print()
    print("="*100)
    print()
    #CreateConfigs(data_path=data_path, input_dir="data_selected_columns", output_dir="configs").run()
    # main_config_file_path = data_path / "configs" / "config_2.csv"
    '''
    input_address = source
    outut_address = destination
    total_btc + fees = measure
    time_step = timestamp
    '''
    #run_static_graph(main_config_file_path)
    #run_temporal_graph(main_config_file_path)
    #run_join_feature_files()
    #run_callmine_focus(1)
    #run_callmine_focus(2)

    from collections import Counter

    print("Calculating scores...")
    scores_sorted = sorted_gen2out_scores(read_if_cached=False, is_to_save=True)
    print("Scores calculated")
    # print(scores_sorted[:100])
    address_to_class = get_address_class_lookup()
    value_counts = Counter(address_to_class.values())
    print("Class distribution in address_to_class:", value_counts)
    print("len() address_to_class:", len(address_to_class))

    print("Calculating metrics...")
    metrics = Metrics(scores_sorted=scores_sorted, address_to_class=address_to_class)
    metrics.print_metrics()
    print('==='*40)
    print('==='*40)
    print('==='*40)
    metrics.scores_profile_from_positive_class()
    metrics.plot_all_graphs()
    print("Metrics calculated.")
    # p_at_10 = precision_at_k(scores_sorted, address_to_class, k=10)
    # p_at_50 = precision_at_k(scores_sorted, address_to_class, k=50)

    # print("Precision@10:", p_at_10)
    # print("Precision@50:", p_at_50)

    '''
    - [Done] Criar data raw
    - [Done] Criar data com colunas selecionadas -> data_selected_columns
    - [Done] Validar data_selected_columns
    - Preciso organizar o código para conseguir exportar um relatório de validação
    - Também preciso organizar as premissas e explicar por que é okay utilizar o dataset para minha análise
    - [Done] Criar datasets com as 3 configs
    - [Done] Rodar call_mine nos datasets criados - 1h
    - Analisar resultados - 1~2h --> entendi nada

    # * [ ] computar score por wallet --> tenho que definir com base no que o call_mine retorna e salva no computador
    # * [ ] gerar ranking -> 30 min e já tenho snippet pronto
    # * [ ] avaliar Precision@K -> 30 min mas ia cospe snippet mt rápido

    - tenho que fazer uma análise exploratoria pra complementar essas validações
    - também preciso extrair as features mais importantes e rodar 2 classificadores
    '''
