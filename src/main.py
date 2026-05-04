from src.extract import Extract
from src.validations import Validations
from src.metrics import Metrics
from src.metrics_a import MetricsA
from src.algorithms import gen2out_scores_from_setups, run_callmine_setups
from src.extract_selected_columns import Standardization
from src.analysis import SimpleCharts
from callmine.callmine_focus.run_callmine_focus import runGen2Out
from callmine.callmine_focus.run_callmine_focus import call_mine_main
from src.transform import CreateConfigs, FeatureEngineering
import numpy as np
import pandas as pd
from config import Config
from pathlib import Path
import os


def print_data_types(file_path):
    if not file_path.exists():
        print(f"  ✗ Warning: not found {file_path}")
        return

    print(f"  ✓ Data types:")
    df = pd.read_csv(file_path)
    for col in df.columns:
        print(f"{col}: {df[col].dtype}")

    print("-" * 40)
    print()

def run_transformation():
    '''
    Aqui com o config_features.csv posso fazer toda análise exploratória
    Para novos conjuntos de features para rodar os modelos, posso exportar csvs diferentes... (config_features_1.csv, config_features_2.csv, etc)
    '''
    path = Config.data_path / "configs"
    if os.path.exists(path) and os.listdir(path):
        print(f"\n✓ Folder '{path}' already exists and is not empty. Skipping download.")
        return
    
    CreateConfigs(data_path=Config.data_path, input_dir="data_selected_columns", output_dir="configs").run()
    FeatureEngineering().base_config()
    FeatureEngineering().generate_first_config()
    FeatureEngineering().generate_second_config()
    FeatureEngineering().generate_third_config()
    FeatureEngineering().generate_fourth_config()
    
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

def run_metrics_a(setup_name, scores_sorted, address_to_class):
    print("Calculating metrics...")
    metrics = MetricsA(
        scores_sorted=scores_sorted, 
        address_to_class=address_to_class, 
        figures_path=Config.figures_path, 
        setup_name=setup_name
    )

    # 1. Primeiro: análise de distribuição de scores (valida inversão)
    metrics.scores_profile()

    # 2. Depois: métricas numéricas
    metrics.print_metrics()

    # 3. Por último: gráficos
    # metrics.plot_all_graphs()

    print("Metrics calculated.")

def validacao_weighted_degrees():
    df = pd.read_csv(Config.path_config)
    df = df[['node_ID', 'weighted_out_degree', 'weighted_in_degree', 'class']]
    in_zerados = df[df['weighted_in_degree'] == 0]
    out_zerados = df[df['weighted_out_degree'] == 0]
    print(in_zerados)
    print(out_zerados)
    print(df['class'].value_counts())

def main(config: Config):
    '''
    Ordem para rodar para pegar os resultados de forma parcial, para não precisar rodar tudo de novo caso queira pegar só um gráfico específico, por exemplo:

    1. [Done] Rodar Extract, Standardization e Validations --> pegar o output de validations. Rodar colocando resultado em um arquivo validations.txt
    2. [Done] Colocar skip true em validations, descomentar run_transformation e SimpleCharts e rodar;
    3. [Done] Comentar SimpleCharts, descomentar run_callmine_setups e rodar;
        - [Done] c1_d2 --> pegar os gráficos e guardar em uma pasta. Remover do repo raiz do callmine
        - [Done] c2_d2 --> pegar os gráficos e guardar em uma pasta. Remover do repo raiz do callmine
    4. [Done] Comentar run_callmine_setups, descomentar gen2out_scores_from_setups e rodar colocando resultado em um arquivo gen2out_scores.txt
    '''
    Extract(data_path=Config.data_path, folder_id=Config.google_drive_folder_id, output_dir="raw").run()

    Standardization(data_path=Config.data_path, input_dir="raw", output_dir="data_selected_columns").run()
    
    Validations(data_path=Config.data_path, skip=True).run()
    
    # run_transformation()

    os.makedirs(Config.figures_path, exist_ok=True)
    
    # SimpleCharts(config_features_path=Config.path_config, figures_path=Config.figures_path).run()
    
    # # validacao_weighted_degrees()

    # run_callmine_setups(Config.CallMine.setups)
    
    scores_sorted = gen2out_scores_from_setups(read_if_cached=False, is_to_save=False)
    address_to_class = get_address_class_lookup()

    print()
    for setup, scores in scores_sorted.items():
        print('='*40)
        print(f"Running metrics for {setup} scores")
        print('='*40)
        run_metrics_a(setup, scores, address_to_class)
