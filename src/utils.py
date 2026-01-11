import pandas as pd


def print_data_types(file_path):
    if not file_path.exists():
        print(f"  ✗ Warning: not found {file_path}")
        return

    print(f"  ✓ Data types:")
    df = pd.read_csv(file_path)
    for col in df.columns:
        print(f"{col}: {df[col].dtype}")

    print("-" * 40)
    print()