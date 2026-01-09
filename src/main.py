from src.extract import ExtractFromDrive
from src.selected_columns import SelectColumns
from src.validations import Validations
from src.create_configs import CreateConfigs
from callmine.tgraph.static_graph import StaticGraph
from callmine.tgraph.temporal_graph import TemporalGraph
from callmine.tgraph.join_feature_files import JoinFeatures
from callmine.callmine_focus.run_callmine_focus import call_mine_main
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
    main_config_file_path = data_path / "configs" / "config_2.csv"
    '''
    input_address = source
    outut_address = destination
    total_btc + fees = measure
    time_step = timestamp
    '''
    #run_static_graph(main_config_file_path)
    # run_temporal_graph(main_config_file_path)
    #run_join_feature_files()
    run_callmine_focus(1)
    # run_callmine_focus(2)

    '''
    - [Done] Criar data raw
    - [Done] Criar data com colunas selecionadas -> data_selected_columns
    - [Done] Validar data_selected_columns
    - Preciso organizar o código para conseguir exportar um relatório de validação
    - Também preciso organizar as premissas e explicar por que é okay utilizar o dataset para minha análise
    - [Done] Criar datasets com as 3 configs
    - Rodar call_mine nos datasets criados - 1h
    - Analisar resultados - 1~2h

    # * [ ] computar score por wallet --> tenho que definir com base no que o call_mine retorna e salva no computador
    # * [ ] gerar ranking -> 30 min e já tenho snippet pronto
    # * [ ] avaliar Precision@K -> 30 min mas ia cospe snippet mt rápido

    - tenho que fazer uma análise exploratoria pra complementar essas validações
    - também preciso extrair as features mais importantes e rodar 2 classificadores
    '''
