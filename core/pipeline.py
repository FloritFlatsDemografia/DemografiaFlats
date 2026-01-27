import pandas as pd

from core.io_readers import read_any
from core.cleaning import clean_lista_reservas, clean_listado_reservas


def _ensure_date_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garantiza que existan:
      - Fecha_alta
      - Fecha_entrada
    aunque vengan como 'Fecha alta', 'Fecha entrada', o con sufijo _mkt.
    """
    df = df.copy()

    # candidatos por prioridad
    mapping_candidates = {
        "Fecha_alta": ["Fecha_alta", "Fecha alta", "Fecha_alta_mkt", "Fecha alta_mkt"],
        "Fecha_entrada": ["Fecha_entrada", "Fecha entrada", "Fecha_entrada_mkt", "Fecha entrada_mkt"],
        "Fecha_salida": ["Fecha_salida", "Fecha salida", "Fecha_salida_mkt", "Fecha salida_mkt"],
    }

    for target, cands in mapping_candidates.items():
        if target in df.columns:
            continue
        for c in cands:
            if c in df.columns:
                df[target] = df[c]
                break

    # parseo seguro a datetime si existen
    for c in ["Fecha_alta", "Fecha_entrada", "Fecha_salida"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)

    return df


def load_and_prepare(f_lista, f_listado) -> pd.DataFrame:
    """
    Une:
      - Lista reservas (ingresos)
      - Listado reservas (pais/provincia/idioma/portal)
    por Localizador.
    """
    df_lista_raw = read_any(f_lista)
    df_listado_raw = read_any(f_listado)

    df_lista = clean_lista_reservas(df_lista_raw)
    df_listado = clean_listado_reservas(df_listado_raw)

    # LEFT JOIN: mantenemos todas las reservas con dinero (lista)
    df = df_lista.merge(df_listado, on="Localizador", how="left", suffixes=("", "_mkt"))

    # Normaliza columnas de fechas (evita KeyError)
    df = _ensure_date_cols(df)

    # Lead time (días entre reserva y entrada) si hay datos
    if "Fecha_entrada" in df.columns and "Fecha_alta" in df.columns:
        df["Lead_time_dias"] = (df["Fecha_entrada"] - df["Fecha_alta"]).dt.days
        df.loc[df["Lead_time_dias"] < 0, "Lead_time_dias"] = pd.NA
    else:
        df["Lead_time_dias"] = pd.NA

    # Mes (para estacionalidad)
    if "Fecha_entrada" in df.columns:
        df["Mes"] = df["Fecha_entrada"].dt.to_period("M").dt.to_timestamp()
    else:
        df["Mes"] = pd.NaT

    # Asegura columnas marketing para que no rompan dashboards
    for col in ["Pais", "Provincia", "Idioma", "Portal", "Origen_marketing"]:
        if col not in df.columns:
            df[col] = pd.NA

    return df
