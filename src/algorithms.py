from callmine.callmine_focus.run_callmine_focus import runGen2Out
from callmine.callmine_focus.run_callmine_focus import call_mine_main
from config import Config
from pathlib import Path
import numpy as np
import pandas as pd

"""
CALLMINE!!
"""
def run_callmine_focus(setup):
    print("Running callmine with the following setup:")
    print(setup)
    print()
    call_mine_main(('dummy', *setup.values()))
    print("Callmine ended.")
    print("="*40)

def run_callmine_setups(setups:dict):
    for setup_name, setup in setups.items():
        print(f'Running setup: {setup_name}')
        run_callmine_focus(setup)

"""
GEN2OUT
"""
def gen2out_scores(scores_path: Path, path_features:Path, read_if_cached=False):
    if scores_path.exists() and read_if_cached:
        print(f"Reading cached Gen2Out scores from: {scores_path}")
        df_scores = pd.read_csv(scores_path)
        return list(zip(df_scores['node_ID'], df_scores['anomaly_score']))

    df_features = pd.read_csv(path_features)
    if Config.remove_unknown_from_config:
        df_features = df_features[df_features['class'] != 3]
        
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
    df_features = df_features[['node_ID'] + keys].set_index('node_ID').reset_index()
    
    return runGen2Out(ids = df_features['node_ID'],
                            features = np.asarray(df_features[keys], dtype = float),
                            option=1)
    

def gen2out_setup_scores(scores_path: Path, path_features:Path, read_if_cached=False, is_to_save=False, inverted=False):
    '''
    Posso transformar isso daqui em uma classe para testar diferentes chaves em diferentes algoritmos de detecção de anomalia
    '''
    scores = gen2out_scores(scores_path=scores_path, path_features=path_features, read_if_cached=read_if_cached)
    
    if inverted:
        scores = [(node_id, 1- score) for node_id, score in scores] #invertendo valores de score

    if is_to_save:
        df_scores = pd.DataFrame(scores, columns=["node_ID", "anomaly_score"])
        df_scores.to_csv(scores_path, index=False)
        print(f"Gen2Out sorted scores saved to: {scores_path}")

    return scores

def gen2out_scores_from_setups(configs=Config.path_configs, read_if_cached=False, is_to_save=False, inverted=False):
    scores = {}
    for name, path in configs.items():
        print(f"Running gen2out scores for setup {name}...")
        score_path_to_save = Config.data_path / f"{name}_gen2out_sorted.csv"
        score = gen2out_setup_scores(
            scores_path=score_path_to_save,
            path_features=path,
            read_if_cached=read_if_cached,
            is_to_save=is_to_save,
            inverted=inverted
        )
        scores[name] = score    
    return scores
