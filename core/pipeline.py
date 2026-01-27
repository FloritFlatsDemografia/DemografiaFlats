import pandas as pd

from core.io_readers import read_any
from core.cleaning import clean_lista_reservas, clean_listado_reservas


def load_and_prepare(f_lista, f_listado) -> pd.DataFrame:
    """
    Une:
      - Lista reservas (ingresos)
      - Listado reservas (pais/provincia/idioma/portal)
    por Localizador.
    Devuelve dataset final para dashboards.
    """
    df_lista_raw = read_any(f_lista)
    df_listado_raw = read_any(f_listado)

    df_lista = clean_lista_reservas(df_lista_raw)
    df_listado = clean_listado_reservas(df_listado_raw)

    # LEFT JOIN: mantenemos todas las reservas con dinero (lista), y traemos atributos de marketing
    df = df_lista.merge(df_listado, on="Localizador", how="left", suffixes=("", "_mkt"))

    # Lead time (ventana de reserva): Fecha_entrada - Fecha_alta (si ambas existen)
    df["Lead_time_dias"] = (df["Fecha_entrada"] - df["Fecha_alta"]).dt.days
    df.loc[df["Lead_time_dias"] < 0, "Lead_time_dias"] = pd.NA

    # Mes (para estacionalidad)
    df["Mes"] = df["Fecha_entrada"].dt.to_period("M").dt.to_timestamp()

    # Normalizaciones finales para que no rompa gráficos
    for col in ["Pais", "Provincia", "Idioma", "Portal", "Origen_marketing"]:
        if col not in df.columns:
            df[col] = pd.NA

    return df
