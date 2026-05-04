from pathlib import Path


class Config:
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
    google_drive_folder_id = "1MRPXz79Lu_JGLlJ21MDfML44dKN9R08l"
    
    src_path = Path(__file__).parent / "src"
    data_path = src_path / "data"

    figures_path = data_path / "figures"
    configs_path = Path(__file__).parent/ "src" / "data" / "configs"
    
    path_config = configs_path / "config_features.csv"
    path_config_1 = configs_path / "config_features_1.csv"
    path_config_2 = configs_path / "config_features_2.csv"
    path_config_3 = configs_path / "config_features_3.csv"
    path_config_4 = configs_path / "config_features_4.csv"

    path_configs = {
        "config_1": path_config_1,
        "config_2": path_config_2,
        # "config_3": path_config_3,
        # "config_4": path_config_4
    }
    remove_unknown_from_config = False
    class Classes:
        ILLICIT = 1
        LICIT = 2
        UNKNOWN = 3
    
    class CallMine:
        setups = {
            # 'c1_d2': {
            #     'path_features' : Path(__file__).parent/ "src" / "data" / "configs" / "config_features_1.csv",
            #     'detection_option' : 1,
            #     'num_outliers' : 30,
            #     'budget' : 10,
            #     'dimensionality' : 2,
            #     'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            # },

            'c2_d2': {
                'path_features' : Path(__file__).parent/ "src" / "data" / "configs" / "config_features_2.csv",
                'detection_option' : 1,
                'num_outliers' : 30,
                'budget' : 10,
                'dimensionality' : 2,
                'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            },

            # 'c1_d3': {
            #     'path_features' : Path(__file__).parent/ "src" / "data" / "configs" / "config_features_1.csv",
            #     'detection_option' : 1,
            #     'num_outliers' : 10,
            #     'budget' : 5,
            #     'dimensionality' : 3, # <<- the only difference
            #     'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            # },
            # 'c2_d3': {
            #     'path_features' : Path(__file__).parent/ "src" / "data" / "configs" / "config_features_2.csv",
            #     'detection_option' : 1,
            #     'num_outliers' : 10,
            #     'budget' : 5,
            #     'dimensionality' : 3,
            #     'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            # }
        }
