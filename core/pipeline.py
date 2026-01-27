from core.cleaning import clean_listado_reservas
from core.io_readers import read_any


def load_and_prepare(f_lista, f_listado):
    """
    Carga y limpia los archivos de reservas.
    """

    # Solo usamos LISTADO (el que tiene fechas, ingresos, etc.)
    df = clean_listado_reservas(read_any(f_listado))

    return df
