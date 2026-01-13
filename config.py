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

    class Classes:
        ILICITA = 1
        LICITA = 2
        UNKNOWN = 3
    
    class CallMine:
        setups = {
            'c1_d2': {
                'path_features' : Path(__file__).parent/ "src" / "data" / "config_features_1.csv",
                'detection_option' : 1,
                'num_outliers' : 10,
                'budget' : 5,
                'dimensionality' : 2,
                'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            },
            'c1_d3': {
                'path_features' : Path(__file__).parent/ "src" / "data" / "config_features_1.csv",
                'detection_option' : 1,
                'num_outliers' : 10,
                'budget' : 5,
                'dimensionality' : 3, # <<- the only difference
                'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            },
            'c2_d2': {
                'path_features' : Path(__file__).parent/ "src" / "data" / "config_features_2.csv",
                'detection_option' : 1,
                'num_outliers' : 10,
                'budget' : 5,
                'dimensionality' : 2,
                'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            },
            'c2_d3': {
                'path_features' : Path(__file__).parent/ "src" / "data" / "config_features_2.csv",
                'detection_option' : 1,
                'num_outliers' : 10,
                'budget' : 5,
                'dimensionality' : 3,
                'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            }
        }
