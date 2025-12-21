from src.extract import ExtractFromDrive
from pathlib import Path
import pandas as pd

files = [
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
    
    for file in files:
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
    '''
    - Criar data raw
    - Criar data com colunas selecionadas -> data_selected_columns

    - Verificar se a wallets_features_classes_combined.csv está consistente com a wallets_features.csv e wallets_classes.csv
        - Verificar conjunto de colunas
        - Verificar conjunto de carteiras com count se ta tudo igual
        - Verificar se a carteira + ilicito está batendo com wallet_classes.csv
    
    - Verificar se a tabela AddrAddr_edgelist.csv está consistente com a TxAddr_edgelist.csv e a AddrTx_edgelist.csv
        - Se tiver, podemos usar a AddrAddr_edgelist.csv

    - Verificar se toda transação ilicita foi feita por um endereço ilicito
        agregar as tabelas AddrTx_edgelist e TxAddr_edgelist
        - Para cada transação na txs_classes.csv que for ilicita:
            - Verificar se algum dos endereços de entrada ou saída é ilicito

    - Entender se uma transação pode ser feita entre vários endereços de entrada e vários de saída???
        - Da pra fazer isso com a AddrTx_edgelist e TxAddr_edgelist, dai validando com a txs_features com in and out
        - Para cada transação no trx_features que tiver in_txs_degree e out_txs_degree maior que 1:
            - Verificar a qtd de endereços na AddrTx_edgelist para aquela transação coincidem com in_txs_degree
            - Verificar a qtd de endereços na TxAddr_edgelist para aquela transação coincidem com out_txs_degree

    ---
    Terminado as validações acima, partir para criação dos datasets para rodar o call_mine
    - Criar datasets com as 3 configs
    - Rodar call_mine nos datasets criados - 1h
    - Analisar resultados - 1~2h
    
    '''
    ExtractFromDrive(data_path=data_path).run()
    # print_data_types()


    # Validações dos dados - 2h
    # Criação dos datasets de cenários call_mine - 30 min
    # Rodar call_mine nos datasets criados - 1h
    # Analisar resultados - 1~2h
    # * [ ] computar score por wallet --> tenho que definir com base no que o call_mine retorna e salva no computador
    # * [ ] gerar ranking -> 30 min e já tenho snippet pronto
    # * [ ] avaliar Precision@K -> 30 min mas ia cospe snippet mt rápido
    