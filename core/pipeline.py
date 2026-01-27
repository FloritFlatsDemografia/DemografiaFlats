from core.io_readers import read_any
from core.cleaning import clean_listado_reservas


def load_and_prepare(f_lista, f_listado):
    df = clean_listado_reservas(read_any(f_listado))
    return df
