import pandas as pd

from core.cleaning import clean_df
from core.io_readers import read_file


def load_and_prepare(file) -> pd.DataFrame:
    """
    Carga archivo (CSV / XLS / XLSX) y aplica limpieza estándar
    """
    df = read_file(file)
    df = clean_df(df)
    return df
