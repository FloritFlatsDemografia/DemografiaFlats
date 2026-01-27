import pandas as pd
from core.io_readers import read_file
from core.cleaning import clean_df


def load_and_prepare(file) -> pd.DataFrame:
    df = read_file(file)
    df = clean_df(df)
    return df
