from __future__ import annotations

import re
import numpy as np
import pandas as pd


def _fix_mojibake(s: str) -> str:
    """
    Arregla textos típicos rotos por encoding: EspaÃ±a -> España, PaÃ­s -> País, etc.
    Si no aplica, devuelve el string original.
    """
    if not isinstance(s, str) or not s:
        return s
    try:
        # caso típico: texto UTF-8 leído como latin1/cp1252
        repaired = s.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
        if repaired and repaired != s:
            return repaired
    except Exception:
        pass
    return s


def _norm_colname(c: str) -> str:
    c = _fix_mojibake(str(c))
    c = c.strip()
    c = re.sub(r"\s+", " ", c)
    return c


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_norm_colname(c) for c in df.columns]

    # arreglar valores en columnas objeto
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].map(_fix_mojibake)
    return df


def _pick_first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _to_datetime_series(s: pd.Series) -> pd.Series:
    # dayfirst=True porque tus fechas suelen ser dd/mm/yyyy
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


def _to_number_series(s: pd.Series) -> pd.Series:
    """
    Convierte números con coma/punto y símbolos €.
    """
    if s is None:
        return pd.Series(dtype="float64")
    s = s.astype(str)
    s = s.str.replace("€", "", regex=False).str.replace("\xa0", " ", regex=False).str.strip()
    # si viene "9.775.712" o "9,775,712"
    s = s.str.replace(".", "", regex=False)  # quita miles
    s = s.str.replace(",", ".", regex=False)  # coma decimal -> punto
    return pd.to_numeric(s, errors="coerce")


def clean_lista_reservas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Excel 1: "Lista reservas"
    Columnas clave (según tu descripción):
    - Localizador
    - Fecha alta
    - Fecha entrada
    - Fecha salida
    - Alojamiento (o Nombre del alojamiento)
    - Total reserva (€) (puede venir como 'Total reserva (â‚¬)')
    """
    df = _normalize_dataframe(df)

    col_localizador = _pick_first_existing(df, ["Localizador", "Localizador agente", "Localizador agente "])
    col_aloj = _pick_first_existing(df, ["Alojamiento", "Nombre alojamiento", "Nombre del alojamiento"])
    col_alta = _pick_first_existing(df, ["Fecha alta", "Fecha creación", "Fecha reserva"])
    col_in = _pick_first_existing(df, ["Fecha entrada", "Entrada"])
    col_out = _pick_first_existing(df, ["Fecha salida", "Salida"])
    col_ing = _pick_first_existing(
        df,
        ["Total reserva (€)", "Total reserva (€)", "Total reserva", "Total reserva (â‚¬)", "Total reserva (EUR)"],
    )

    out = pd.DataFrame()
    if not col_localizador:
        raise ValueError("❌ En 'Lista reservas' no encuentro la columna 'Localizador'.")

    out["Localizador"] = df[col_localizador].astype(str).str.strip()

    if col_aloj:
        out["Alojamiento"] = df[col_aloj].astype(str).str.strip()
    if col_alta:
        out["Fecha alta"] = _to_datetime_series(df[col_alta])
    if col_in:
        out["Fecha entrada"] = _to_datetime_series(df[col_in])
    if col_out:
        out["Fecha salida"] = _to_datetime_series(df[col_out])

    if col_ing:
        out["Ingreso"] = _to_number_series(df[col_ing])
    else:
        out["Ingreso"] = np.nan  # se podrá completar desde el Excel 2 si existe

    return out


def clean_listado_reservas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Excel 2: "Listado de reservas"
    Columnas relevantes:
    - Localizador
    - Fecha alta
    - Fecha entrada / Fecha salida
    - noches
    - Adultos, Niños, Bebés
    - Nombre alojamiento
    - Cliente: País
    - Ocupante: Provincia
    - Ocupante: País
    - Ocupante: Idioma del cliente
    - Portal
    - (opcional) Total reserva con tasas (si un día quieres usarlo)
    """
    df = _normalize_dataframe(df)

    col_localizador = _pick_first_existing(df, ["Localizador"])
    if not col_localizador:
        raise ValueError("❌ En 'Listado de reservas' no encuentro la columna 'Localizador'.")

    col_alta = _pick_first_existing(df, ["Fecha alta"])
    col_in = _pick_first_existing(df, ["Fecha entrada"])
    col_out = _pick_first_existing(df, ["Fecha salida"])
    col_noches = _pick_first_existing(df, ["noches", "Noches"])
    col_adultos = _pick_first_existing(df, ["Adultos"])
    col_ninos = _pick_first_existing(df, ["Niños", "NiÃ±os"])
    col_bebes = _pick_first_existing(df, ["Bebés", "BebÃ©s"])
    col_aloj = _pick_first_existing(df, ["Nombre alojamiento", "Alojamiento", "Nombre del alojamiento"])
    col_pais_cliente = _pick_first_existing(df, ["Cliente: País", "Cliente: PaÃ­s"])
    col_pais_ocup = _pick_first_existing(df, ["Ocupante: País", "Ocupante: PaÃ­s"])
    col_prov = _pick_first_existing(df, ["Ocupante: Provincia", "Provincia"])
    col_idioma = _pick_first_existing(df, ["Ocupante: Idioma del cliente", "Idioma del cliente"])
    col_portal = _pick_first_existing(df, ["Portal"])
    col_total_con_tasas = _pick_first_existing(df, ["Total reserva con tasas", "Total reserva con tasas "])

    out = pd.DataFrame()
    out["Localizador"] = df[col_localizador].astype(str).str.strip()

    if col_alta:
        out["Fecha alta"] = _to_datetime_series(df[col_alta])
    if col_in:
        out["Fecha entrada"] = _to_datetime_series(df[col_in])
    if col_out:
        out["Fecha salida"] = _to_datetime_series(df[col_out])

    # noches: si existe lo uso, si no lo calculo
    if col_noches:
        out["Noches"] = pd.to_numeric(df[col_noches], errors="coerce")
    else:
        out["Noches"] = np.nan

    if col_adultos:
        out["Adultos"] = pd.to_numeric(df[col_adultos], errors="coerce")
    if col_ninos:
        out["Niños"] = pd.to_numeric(df[col_ninos], errors="coerce")
    if col_bebes:
        out["Bebés"] = pd.to_numeric(df[col_bebes], errors="coerce")

    if col_aloj:
        out["Alojamiento"] = df[col_aloj].astype(str).str.strip()

    # País: prioriza Cliente: País; si no, Ocupante: País
    pais = None
    if col_pais_cliente:
        pais = df[col_pais_cliente]
    if col_pais_ocup:
        pais = df[col_pais_ocup] if pais is None else pais.fillna(df[col_pais_ocup])
    if pais is not None:
        out["País"] = pais.astype(str).str.strip().replace({"": np.nan})

    if col_prov:
        out["Provincia"] = df[col_prov].astype(str).str.strip().replace({"": np.nan})

    if col_idioma:
        out["Idioma"] = df[col_idioma].astype(str).str.strip().replace({"": np.nan})

    if col_portal:
        out["Portal"] = df[col_portal].astype(str).str.strip().replace({"": np.nan})

    # (Opcional) ingreso alternativo desde listado si algún día lo quieres
    if col_total_con_tasas:
        out["Ingreso_listado"] = _to_number_series(df[col_total_con_tasas])
    else:
        out["Ingreso_listado"] = np.nan

    # Si no hay noches, intento calcularlas si hay fechas
    if "Fecha entrada" in out.columns and "Fecha salida" in out.columns:
        calc = (out["Fecha salida"] - out["Fecha entrada"]).dt.days
        out["Noches"] = out["Noches"].fillna(calc)

    return out
