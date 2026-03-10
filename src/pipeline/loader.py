import pandas as pd

def load_kaggle_dataset(filepath: str) -> pd.DataFrame:
    """
    Loads historical Kaggle dataset into a dataframe.
    """
    return pd.read_csv(filepath)

