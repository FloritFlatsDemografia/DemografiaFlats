import pandas as pd

def add_money_and_nights(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    # 1) Fechas (K: Fecha entrada, L: Fecha salida)
    # En tu archivo parecen venir como dd/mm/yyyy
    if "Fecha entrada" in d.columns:
        d["Fecha entrada"] = pd.to_datetime(d["Fecha entrada"], dayfirst=True, errors="coerce")
    if "Fecha salida" in d.columns:
        d["Fecha salida"] = pd.to_datetime(d["Fecha salida"], dayfirst=True, errors="coerce")

    # 2) Noches = salida - entrada
    if ("Fecha entrada" in d.columns) and ("Fecha salida" in d.columns):
        d["Noches"] = (d["Fecha salida"] - d["Fecha entrada"]).dt.days
        d.loc[d["Noches"] < 0, "Noches"] = pd.NA  # seguridad

    # 3) Ingresos (columna M en tu Excel) -> columna estándar
    # En tu captura la cabecera parece "Total reserva ..."
    ingreso_col = None
    for c in d.columns:
        if isinstance(c, str) and c.strip().lower().startswith("total reserva"):
            ingreso_col = c
            break

    if ingreso_col:
        d["Total ingresos"] = pd.to_numeric(d[ingreso_col], errors="coerce")
    elif "Total ingresos" in d.columns:
        d["Total ingresos"] = pd.to_numeric(d["Total ingresos"], errors="coerce")

    return d
