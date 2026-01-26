from config import Config # TODO remover e injetar
from .create_config import CreateConfigs
from .features import FeatureEngineering
from .treatment import Treatment

def run_transformation():
    '''
    Aqui com o config_features.csv posso fazer toda análise exploratória
    Para novos conjuntos de features para rodar os modelos, posso exportar csvs diferentes... (config_features_1.csv, config_features_2.csv, etc)
    '''
    CreateConfigs(data_path=Config.data_path, input_dir="data_selected_columns", output_dir="configs").run()
    FeatureEngineering().base_config()
    Treatment().run()
