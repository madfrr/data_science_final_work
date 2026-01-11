from callmine.tgraph.static_graph import StaticGraph
from callmine.tgraph.temporal_graph import TemporalGraph
from callmine.tgraph.join_feature_files import JoinFeatures
from callmine.callmine_focus.run_callmine_focus import call_mine_main
from config import Config
from pathlib import Path

'''
[TODO] Talvez juntar essa parte de run static, temporal e join feature files com a parte de criação de configs
Ai eu crio os datasets com as features processadas pra rodar tanto o callmine, detector de anomalia e outros classificadores!!!
GG
'''
def run_static_graph(main_config_file_path: Path):
    print("Running callmine static_graph...")
    static_graph = StaticGraph(filename=main_config_file_path)
    static_graph_output_path = Config.data_path / "nodeVectors.csv"
    static_graph.print_to_csv(static_graph_output_path)
    static_graph.my_print()
    print(f"Static graph node vectors saved to: {static_graph_output_path}")

    return static_graph.df_nodes

def run_temporal_graph(main_config_file_path: Path):
    print("Running callmine temporal_graph...")
    temporal_graph = TemporalGraph(filename=main_config_file_path)
    temporal_graph_output_path = Config.data_path / "t_nodeVectors.csv"
    temporal_graph.print_to_csv(temporal_graph_output_path)
    temporal_graph.my_print()
    print(f"Temporal graph node vectors saved to: {temporal_graph_output_path}")

    return temporal_graph.df_nodes

def run_join_feature_files():
    print("Running callmine join_features...")
    temporal_graph_path = Config.data_path / "t_nodeVectors.csv"
    static_graph_path = Config.data_path / "nodeVectors.csv"
    join_features_output_path = Config.data_path / "config_features_1.csv"

    join_features = JoinFeatures(path_temporal=temporal_graph_path, path_static=static_graph_path)
    join_features.print_to_csv(join_features_output_path)
    print(f"Joined features saved to: {join_features_output_path}")

    return join_features.df_all

def run_callmine_focus(setup):
    print("Running callmine with the following setup:")
    print(setup)
    print()
    call_mine_main(('dummy', *setup.values()))
    print("Callmine ended.")
    print("="*40)

def run_callmine_steps(setup, generate_features=False):
    if generate_features:
        run_static_graph()
        run_temporal_graph()
        run_join_feature_files()
    run_callmine_focus(setup)