import pandas as pd

from core.cleaning import clean_df
from core.io_readers import read_any


def load_and_prepare(file) -> pd.DataFrame:
    """
    Carga archivo (CSV / XLS / XLSX) y aplica limpieza estándar
    """
    df = read_any(file)
    df = clean_df(df)
    return df
