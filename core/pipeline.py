import pandas as pd
from core.io_readers import read_any
from core.cleaning import clean_lista_reservas, clean_listado_reservas


def load_and_prepare(f_lista, f_listado) -> pd.DataFrame:
    """
    Une ambos excels por Localizador y calcula métricas:
    - Noches (si no vienen, se calculan por fechas)
    - ADR = Ingresos / Noches
    - Lead_time_dias = Fecha_entrada - Fecha_alta
    """
    df_lista = clean_lista_reservas(read_any(f_lista))
    df_listado = clean_listado_reservas(read_any(f_listado))

    df = df_lista.merge(df_listado, on="Localizador", how="left")

    # Noches: prioriza campo "Noches" del listado; si no, calcula por fechas
    if "Noches" not in df.columns:
        df["Noches"] = pd.NA

    if df["Noches"].isna().all():
        if "Fecha_entrada" in df.columns and "Fecha_salida" in df.columns:
            noches_calc = (df["Fecha_salida"] - df["Fecha_entrada"]).dt.days
            df["Noches"] = noches_calc
        else:
            df["Noches"] = pd.NA

    # Asegura Noches numérico y válido
    df["Noches"] = pd.to_numeric(df["Noches"], errors="coerce")
    df.loc[df["Noches"] <= 0, "Noches"] = pd.NA

    # ADR
    df["ADR"] = pd.NA
    if "Ingresos" in df.columns:
        df["ADR"] = df["Ingresos"] / df["Noches"]

    # Lead time (NO puede romper nunca)
    df["Lead_time_dias"] = pd.NA
    if "Fecha_entrada" in df.columns and "Fecha_alta" in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df["Fecha_entrada"]) and pd.api.types.is_datetime64_any_dtype(df["Fecha_alta"]):
            lt = (df["Fecha_entrada"] - df["Fecha_alta"]).dt.days
            lt = lt.where(lt >= 0)
            df["Lead_time_dias"] = lt

    # Mes para gráficos
    df["Mes"] = pd.NaT
    if "Fecha_entrada" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Fecha_entrada"]):
        df["Mes"] = df["Fecha_entrada"].dt.to_period("M").dt.to_timestamp()

    # Columnas marketing garantizadas (evita petadas en dashboards)
    for c in ["Pais", "Provincia", "Idioma", "Portal", "Origen_marketing", "Alojamiento"]:
        if c not in df.columns:
            df[c] = pd.NA

    return df
