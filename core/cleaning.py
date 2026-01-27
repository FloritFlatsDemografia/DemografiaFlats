import pandas as pd


def clean_lista_reservas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = df.columns.str.strip()

    # Fechas
    for c in ["Fecha entrada", "Fecha salida", "Fecha alta"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)

    # Noches
    if "Fecha entrada" in df.columns and "Fecha salida" in df.columns:
        df["Noches"] = (df["Fecha salida"] - df["Fecha entrada"]).dt.days

    # Ingresos (columna M)
    if "Total reserva" in df.columns:
        df["Ingresos"] = (
            df["Total reserva"]
            .astype(str)
            .str.replace(",", ".")
            .astype(float)
        )

    # ADR
    if "Ingresos" in df.columns and "Noches" in df.columns:
        df["ADR"] = df["Ingresos"] / df["Noches"].replace(0, pd.NA)

    return df


def clean_listado_reservas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()

    rename = {
        "Ocupante: País": "País",
        "Ocupante: Provincia": "Provincia",
        "Ocupante: Idioma del cliente": "Idioma",
        "Ocupante: Adultos": "Adultos",
        "Ocupante: Niños": "Niños",
    }

    for k, v in rename.items():
        if k in df.columns:
            df[v] = df[k]

    keep = ["Localizador", "País", "Provincia", "Idioma", "Adultos", "Niños"]
    return df[[c for c in keep if c in df.columns]]
