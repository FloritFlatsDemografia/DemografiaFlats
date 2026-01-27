from core.io_readers import read_any
from core.cleaning import clean_lista_reservas, clean_listado_reservas
import pandas as pd


def load_and_prepare(f_lista, f_listado) -> pd.DataFrame:
    df_lista = clean_lista_reservas(read_any(f_lista))
    df_listado = clean_listado_reservas(read_any(f_listado))

    df = df_lista.merge(
        df_listado,
        on="Localizador",
        how="left"
    )

    return df
