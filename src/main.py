from src.extract import ExtractFromDrive
from src.selected_columns import SelectColumns
from src.validations import Validations
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

def main():
    ExtractFromDrive(data_path=data_path).run()
    print()
    print("="*100)
    print()
    # print_data_types()
    SelectColumns(data_path=data_path).run()
    print()
    print("="*100)
    print()
    Validations(data_path=data_path).run()
    print()
    print("="*100)
    print()
    '''
    - [Done] Criar data raw
    - [Done] Criar data com colunas selecionadas -> data_selected_columns
    - [ ] Validar data_selected_columns
    
    - Criar datasets com as 3 configs
    - Rodar call_mine nos datasets criados - 1h
    - Analisar resultados - 1~2h

    # * [ ] computar score por wallet --> tenho que definir com base no que o call_mine retorna e salva no computador
    # * [ ] gerar ranking -> 30 min e já tenho snippet pronto
    # * [ ] avaliar Precision@K -> 30 min mas ia cospe snippet mt rápido
    '''
