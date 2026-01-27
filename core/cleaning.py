import pandas as pd


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalizar nombres de columnas
    df.columns = (
        df.columns.str.strip()
        .str.replace("\n", " ")
        .str.replace("  ", " ")
    )

    # Fechas
    for c in ["Fecha entrada", "Fecha salida", "Fecha alta"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)

    # Noches
    if "Fecha entrada" in df.columns and "Fecha salida" in df.columns:
        df["Noches"] = (df["Fecha salida"] - df["Fecha entrada"]).dt.days

    # Ingresos
    for c in ["Total reserva", "Importe total", "Total reserva (€)"]:
        if c in df.columns:
            df["Ingresos"] = (
                df[c]
                .astype(str)
                .str.replace(",", ".")
                .astype(float)
            )
            break

    # ADR
    if "Ingresos" in df.columns and "Noches" in df.columns:
        df["ADR"] = df["Ingresos"] / df["Noches"].replace(0, pd.NA)

    # Limpieza texto
    for c in ["País", "Provincia", "Idioma", "Portal"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    return df
