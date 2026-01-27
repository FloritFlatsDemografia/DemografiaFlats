import pandas as pd


def _find_col(df, keywords):
    """
    Devuelve la primera columna que contenga TODAS las keywords (case-insensitive)
    """
    for col in df.columns:
        col_low = col.lower()
        if all(k in col_low for k in keywords):
            return col
    return None


def clean_listado_reservas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # --- Detectar columnas clave ---
    col_fecha_entrada = _find_col(df, ["fecha", "entrada"])
    col_fecha_salida = _find_col(df, ["fecha", "salida"])
    col_ingresos = _find_col(df, ["total", "reserva"])

    if not col_fecha_entrada or not col_fecha_salida:
        raise ValueError("❌ No se han encontrado las columnas de Fecha entrada / salida")

    # --- Fechas ---
    df["Fecha entrada"] = pd.to_datetime(
        df[col_fecha_entrada], errors="coerce", dayfirst=True
    )
    df["Fecha salida"] = pd.to_datetime(
        df[col_fecha_salida], errors="coerce", dayfirst=True
    )

    # --- Noches ---
    df["Noches"] = (df["Fecha salida"] - df["Fecha entrada"]).dt.days
    df["Noches"] = df["Noches"].clip(lower=0)

    # --- Ingresos ---
    if col_ingresos:
        df["Ingresos"] = pd.to_numeric(df[col_ingresos], errors="coerce")
    else:
        df["Ingresos"] = 0

    # --- ADR ---
    df["ADR"] = df["Ingresos"] / df["Noches"]
    df["ADR"] = df["ADR"].replace([float("inf"), -float("inf")], 0)

    # --- Normalizar nombres comunes ---
    rename_map = {}
    for c in df.columns:
        cl = c.lower()
        if "pais" in cl:
            rename_map[c] = "País"
        elif "provincia" in cl:
            rename_map[c] = "Provincia"
        elif "idioma" in cl:
            rename_map[c] = "Idioma"

    df = df.rename(columns=rename_map)

    return df
