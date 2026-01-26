'''
- Criar a config
Rodar o Tgraph para pegar as features
merjar com a wallet_features
Fazer o sumário dos dados
Rodar Treatment
fazer as análises exploratórias. Dai vai ser entendendo esse dataset msm e fé. Talvez plotar mais alguma coisa relacionada ao grafo em si qdo gera a config
pra mostrar
'''
import pandas as pd

class Treatment():

    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def remove_duplicates(self, df, subset_columns=None):
        initial_count = len(df)
        df_cleaned = df.drop_duplicates(subset=subset_columns)
        final_count = len(df_cleaned)
        print(f"Removed {initial_count - final_count} duplicate rows based on columns: {subset_columns}")
        return df_cleaned
    
    def remove_nulls(self, df:pd.DataFrame, subset_columns=None):
        initial_count = len(df)
        df_cleaned = df.dropna(subset=subset_columns)
        final_count = len(df_cleaned)
        print(f"Removed {initial_count - final_count} rows with nulls in columns: {subset_columns}")
        return df_cleaned
    
    def min_max_normalize(self, df):
        #TODO usar sklearn
        pass
    
    def remove_unknown_class(self):
        pass

    def run(self):
        print("Running data treatment...")
        
        df = pd.read_csv(self.dataset_path)
        print("Data treatment completed.") 