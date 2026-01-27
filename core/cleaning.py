import pandas as pd


def clean_listado_reservas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalizar nombres
    df.columns = df.columns.str.strip()

    # Fechas
    df["Fecha entrada"] = pd.to_datetime(df["Fecha entrada"], errors="coerce", dayfirst=True)
    df["Fecha salida"] = pd.to_datetime(df["Fecha salida"], errors="coerce", dayfirst=True)

    # Noches
    df["Noches"] = (df["Fecha salida"] - df["Fecha entrada"]).dt.days
    df["Noches"] = df["Noches"].clip(lower=0)

    # Ingresos (columna M)
    ingreso_col = None
    for c in df.columns:
        if "total" in c.lower() and "reserva" in c.lower():
            ingreso_col = c
            break

    if ingreso_col:
        df["Ingresos"] = pd.to_numeric(df[ingreso_col], errors="coerce")
    else:
        df["Ingresos"] = 0

    # ADR
    df["ADR"] = df["Ingresos"] / df["Noches"]
    df["ADR"] = df["ADR"].replace([float("inf"), -float("inf")], 0)

    # Campos estándar
    rename_map = {
        "Pais": "País",
        "Idioma Cliente": "Idioma",
        "Provincia Cliente": "Provincia"
    }

    df = df.rename(columns=rename_map)

    return df
