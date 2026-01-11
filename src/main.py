from src.extract import Extract
from src.validations import Validations
from src.metrics import Metrics
from src.create_configs import CreateConfigs
from callmine.callmine_focus.run_callmine_focus import runGen2Out
from src.callmine_runner import run_callmine_steps
import numpy as np
import pandas as pd
from config import Config

def sorted_gen2out_scores(read_if_cached=False, is_to_save=False):
    '''
    Posso transformar isso daqui em uma classe para testar diferentes chaves em diferentes algoritmos de detecção de anomalia
    '''
    scores_path = Config.data_path / "gen2out_scores_sorted.csv"
    if scores_path.exists() and read_if_cached:
        print(f"Reading cached Gen2Out scores from: {scores_path}")
        df_scores = pd.read_csv(scores_path)
        return list(zip(df_scores['node_ID'], df_scores['anomaly_score']))


    df_features = pd.read_csv(Config.data_path / "allFeatures_nodeVectors.csv")
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
    path = Config.data_path / 'data_selected_columns' / "wallets_classes.parquet"
    df = pd.read_parquet(path, columns=["address", "class"])
    return dict(zip(df["address"], df["class"]))

def run_metrics(scores_sorted, address_to_class):
    print("Calculating metrics...")
    metrics = Metrics(scores_sorted=scores_sorted, address_to_class=address_to_class)
    metrics.print_metrics()
    metrics.scores_profile_from_positive_class()
    metrics.plot_all_graphs()
    print("Metrics calculated.")

def main():
    '''
    input_address = source
    outut_address = destination
    total_btc + fees = measure
    time_step = timestamp
    '''
    Extract(data_path=Config.data_path, folder_id=Config.google_drive_folder_id).run(must_subset_columns=True)
    Validations(data_path=Config.data_path, skip=True).run()
    # -- Tratamento de dados
    # -- análise exploratória tem que ser aqui
    CreateConfigs(data_path=Config.data_path, input_dir="data_selected_columns", output_dir="configs").run()
    run_callmine_steps(Config.call_mine_setup[0], generate_features=Config.CallMine.generate_features)
    run_callmine_steps(Config.call_mine_setup[1], generate_features=False)
    scores_sorted = sorted_gen2out_scores(read_if_cached=False, is_to_save=True)
    address_to_class = get_address_class_lookup()
    run_metrics(scores_sorted, address_to_class)
