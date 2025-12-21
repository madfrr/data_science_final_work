import os
import gdown
from pathlib import Path

class SelectColumns():
    '''
    https://github.com/git-disl/EllipticPlusPlus
    https://drive.google.com/drive/folders/1MRPXz79Lu_JGLlJ21MDfML44dKN9R08l?usp=sharing
    '''

    def __init__(self, data_path, output_dir="data_selected_columns", folder_id="1MRPXz79Lu_JGLlJ21MDfML44dKN9R08l"):
        self.path = data_path / output_dir
        self.folder_id = folder_id
        os.makedirs(output_dir, exist_ok=True)

    def check_if_folder_already_exists(self):
        if os.path.exists(self.path) and os.listdir(self.path):
            print(f"\n✓ Folder '{self.path}' already exists and is not empty. Skipping download.")
            return True
        return False
    
    def run(self):
        pass
