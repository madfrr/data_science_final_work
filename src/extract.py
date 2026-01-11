from extract_selected_columns import SelectColumns
from pathlib import Path
import os
import gdown

class Extract():
    '''
    https://github.com/git-disl/EllipticPlusPlus
    https://drive.google.com/drive/folders/1MRPXz79Lu_JGLlJ21MDfML44dKN9R08l?usp=sharing
    '''

    def __init__(self, data_path, folder_id, output_dir="raw"):
        self.data_path = data_path
        self.path = data_path / output_dir
        self.folder_id = folder_id
        
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)


    def check_if_folder_already_exists(self):
        if os.path.exists(self.path) and os.listdir(self.path):
            print(f"\n✓ Folder '{self.path}' already exists and is not empty. Skipping download.")
            return True
        return False
    
    def extract_raw_data(self):
        print(f"\nStarting download of files to '{self.path}'...")
        if self.check_if_folder_already_exists():
            return
        
        try:
            url = f"https://drive.google.com/drive/folders/{self.folder_id}"
            gdown.download_folder(url, output=self.path, quiet=False, use_cookies=False)
            print("\n✓ All files downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading files: {e}")
            print("\nIf the download fails, you may need to:")
            print("1. Ensure the folder is publicly accessible")
            print("2. Try downloading individual files")
            print("3. Use a browser to download if permissions are required")

        print(f"\nFiles are located in: {os.path.abspath(self.output_dir)}")

    def set_subset_columns(self):
        SelectColumns(data_path=self.data_path).run()

    def run(self, must_subset_columns=False):
        self.extract_raw_data()
        if must_subset_columns:
            self.set_subset_columns()
        