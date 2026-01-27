import pandas as pd


def _norm(s: str) -> str:
    """Normaliza texto para comparar columnas."""
    if not isinstance(s, str):
        return ""
    return (
        s.strip()
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Devuelve el nombre real de la columna que mejor encaje con candidatos.
    candidates: lista de posibles nombres o 'contiene' (heurística).
    """
    cols = list(df.columns)
    cols_norm = {_norm(c): c for c in cols}

    # Match exacto normalizado
    for cand in candidates:
        c_norm = _norm(cand)
        if c_norm in cols_norm:
            return cols_norm[c_norm]

    # Match por "contiene"
    for cand in candidates:
        c_norm = _norm(cand)
        for cn, real in cols_norm.items():
            if c_norm and c_norm in cn:
                return real

    return None


def _to_datetime(series: pd.Series) -> pd.Series:
    # Primero intenta dayfirst (ES), si no, deja NaT
    return pd.to_datetime(series, dayfirst=True, errors="coerce")


def _to_numeric(series: pd.Series) -> pd.Series:
    # Por si viene como texto con comas
    if series.dtype == "O":
        s = series.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        return pd.to_numeric(s, errors="coerce")
    return pd.to_numeric(series, errors="coerce")


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza + estandarización mínima para la app:
    - Detecta columnas de fechas (entrada/salida)
    - Calcula Noches = salida - entrada
    - Detecta Ingresos desde la columna M ("Total reserva...") y crea "Total ingresos"
    - Mantiene el resto de columnas para que filtros/dashboards sigan funcionando
    """
    d = df.copy()

    # 1) Encuentra columnas clave (lo hacemos robusto por si cambian nombres)
    col_entrada = _find_col(d, ["Fecha entrada", "Fecha entrac", "Check-in", "Entrada", "fecha entrada"])
    col_salida = _find_col(d, ["Fecha salida", "Check-out", "Salida", "fecha salida"])
    col_ingresos = _find_col(d, ["Total ingresos", "Total reserva", "Total reserva con tasas", "Total reserva ("])

    # 2) Fechas -> datetime
    if col_entrada:
        d[col_entrada] = _to_datetime(d[col_entrada])
        if col_entrada != "Fecha entrada":
            d = d.rename(columns={col_entrada: "Fecha entrada"})
            col_entrada = "Fecha entrada"

    if col_salida:
        d[col_salida] = _to_datetime(d[col_salida])
        if col_salida != "Fecha salida":
            d = d.rename(columns={col_salida: "Fecha salida"})
            col_salida = "Fecha salida"

    # 3) Noches
    if ("Fecha entrada" in d.columns) and ("Fecha salida" in d.columns):
        d["Noches"] = (d["Fecha salida"] - d["Fecha entrada"]).dt.days
        d.loc[d["Noches"] < 0, "Noches"] = pd.NA  # seguridad

    # 4) Total ingresos
    if col_ingresos:
        d["Total ingresos"] = _to_numeric(d[col_ingresos])
    else:
        # Si no encontró nada, pero ya existía una similar
        if "Total ingresos" in d.columns:
            d["Total ingresos"] = _to_numeric(d["Total ingresos"])

    return d
