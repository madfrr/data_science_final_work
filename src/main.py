from src.extract import Extract
from src.validations import Validations
from src.metrics import Metrics
from src.models import gen2out_scores_from_setups, run_callmine_setups
from src.extract_selected_columns import Standardization
from src.transform import run_transformation
from callmine.callmine_focus.run_callmine_focus import runGen2Out
from callmine.callmine_focus.run_callmine_focus import call_mine_main
import numpy as np
import pandas as pd
from config import Config
from pathlib import Path


def get_address_class_lookup():
    path = Config.data_path / 'data_selected_columns' / "wallets_classes.parquet"
    df = pd.read_parquet(path, columns=["address", "class"])
    return dict(zip(df["address"], df["class"]))

def run_metrics(setup_name, scores_sorted, address_to_class):
    print("Calculating metrics...")
    metrics = Metrics(scores_sorted=scores_sorted, address_to_class=address_to_class, figures_path=Config.figures_path, setup_name=setup_name)
    metrics.print_metrics()
    metrics.scores_profile_from_positive_class()
    metrics.plot_all_graphs()
    print("Metrics calculated.")



def main(config: Config):
    '''
    input_address = source
    outut_address = destination
    total_btc + fees = measure
    time_step = timestamp
    '''
    Extract(data_path=Config.data_path, folder_id=Config.google_drive_folder_id, output_dir="raw").run()

    Standardization(data_path=Config.data_path, input_dir="raw", output_dir="data_selected_columns").run()
    
    Validations(data_path=Config.data_path, skip=True).run()
    
    run_transformation()
    # # -- análise exploratória tem que ser aqui
    
    run_callmine_setups(Config.CallMine.setups)
    
    scores_sorted = gen2out_scores_from_setups(read_if_cached=False, is_to_save=False, inverted=True)
    address_to_class = get_address_class_lookup()
    print()
    for setup, scores in scores_sorted.items():
        print('='*40)
        print(f"Running metrics for {setup} scores")
        print('='*40)
        run_metrics(setup, scores, address_to_class)
