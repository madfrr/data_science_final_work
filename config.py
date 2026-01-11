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
    
    src_dir = Path(__file__).parent / "src"
    data_path = src_dir / "data"

    class Classes:
        ILICITA = 1
        LICITA = 2
        UNKNOWN = 3
    
    class CallMine:
        setups = [
            {
                'path_features' : Path(__file__).parent/ "src" / "data" / "allFeatures_nodeVectors.csv",
                'detection_option' : 1,
                'num_outliers' : 10,
                'budget' : 5,
                'dimensionality' : 2,
                'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            },
            {
                'path_features' : Path(__file__).parent/ "src" / "data" / "allFeatures_nodeVectors.csv",
                'detection_option' : 1,
                'num_outliers' : 10,
                'budget' : 5,
                'dimensionality' : 3, # <<- the only difference
                'output_path' : str(Path(__file__).parent / 'callmine' / 'outputs')
            }
        ]
        generate_features = True