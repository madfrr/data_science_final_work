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

from config import Config

class Treatment():

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def remove_duplicates(self, subset_columns=None):
        initial_count = len(self.df)
        df_cleaned = self.df.drop_duplicates(subset=subset_columns)
        final_count = len(df_cleaned)
        print(f"Removed {initial_count - final_count} duplicate rows based on columns: {subset_columns}")
        self.df = df_cleaned
        return self

    def remove_nulls(self, subset_columns=None):
        initial_count = len(self.df)
        df_cleaned = self.df.dropna(subset=subset_columns)
        final_count = len(df_cleaned)
        print(f"Removed {initial_count - final_count} rows with nulls in columns: {subset_columns}")
        self.df = df_cleaned
        return self
    
    def min_max_normalize(self, df):
        #TODO usar sklearn
        pass
    
    def remove_unknown_class(self):
        initial_count = len(self.df)
        df_cleaned = self.df[self.df['class'] != Config.Classes.UNKNOWN]
        final_count = len(df_cleaned)
        print(f"Removed {initial_count - final_count} rows with UNKNOWN class.")
        self.df = df_cleaned

        return self

    def get_df(self):
        return self.df