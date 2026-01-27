import pandas as pd

from core.io_readers import read_any
from core.cleaning import clean_lista_reservas, clean_listado_reservas


def load_and_prepare(f_lista, f_listado) -> pd.DataFrame:
    """
    Devuelve un dataframe único por reserva (fila = reserva),
    uniendo por Localizador.
    """
    df_lista = clean_lista_reservas(read_any(f_lista))
    df_listado = clean_listado_reservas(read_any(f_listado))

    # Merge: left=LISTADO (tiene país/provincia/idioma/portal/adultos/etc.)
    df = df_listado.merge(
        df_lista[["Localizador", "Ingreso"]],
        on="Localizador",
        how="left",
        suffixes=("", "_lista"),
    )

    # Si no hay ingreso en lista, usar ingreso_listado como fallback
    if "Ingreso_listado" in df.columns:
        df["Ingreso"] = df["Ingreso"].fillna(df["Ingreso_listado"])

    # Asegurar tipos
    if "Ingreso" not in df.columns:
        df["Ingreso"] = pd.NA

    if "Noches" not in df.columns:
        df["Noches"] = pd.NA

    # ADR
    df["ADR"] = pd.to_numeric(df["Ingreso"], errors="coerce") / pd.to_numeric(df["Noches"], errors="coerce")

    # Limpieza final: columnas mínimas para dashboards
    keep = [
        "Localizador",
        "Fecha alta",
        "Fecha entrada",
        "Fecha salida",
        "Alojamiento",
        "Portal",
        "País",
        "Provincia",
        "Idioma",
        "Adultos",
        "Niños",
        "Bebés",
        "Noches",
        "Ingreso",
        "ADR",
    ]
    keep = [c for c in keep if c in df.columns]
    df = df[keep].copy()

    return df
