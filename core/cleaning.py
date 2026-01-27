import re
import unicodedata
import pandas as pd


def _fix_mojibake(text: str) -> str:
    """
    Intenta arreglar strings tipo 'PaÃ­s' -> 'País'.
    Si no puede, devuelve tal cual.
    """
    if not isinstance(text, str):
        return text
    if ("Ã" in text) or ("Â" in text) or ("�" in text):
        try:
            return text.encode("latin1").decode("utf-8")
        except Exception:
            return text
    return text


def _strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def _norm_col(col: str) -> str:
    """
    Normaliza columnas a un formato estable:
    - arregla mojibake
    - minúsculas
    - sin acentos
    - espacios/símbolos -> _
    """
    col = _fix_mojibake(str(col)).strip()
    col = _strip_accents(col).lower()
    col = re.sub(r"[^\w]+", "_", col)
    col = re.sub(r"_+", "_", col).strip("_")
    return col


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_norm_col(c) for c in df.columns]
    return df


def _to_datetime(s):
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


def _to_number(x):
    """
    Convierte números tipo:
      '1.234,56' -> 1234.56
      '860.00'   -> 860.0
      '860,00 €' -> 860.0
    """
    if pd.isna(x):
        return pd.NA
    if isinstance(x, (int, float)):
        return float(x)

    t = str(x)
    t = _fix_mojibake(t)
    t = t.replace("€", "").replace("\xa0", " ").strip()

    # si tiene coma como decimal típico español
    # quitamos miles '.' y cambiamos ',' por '.'
    if "," in t and re.search(r"\d+,\d{1,2}$", t):
        t = t.replace(".", "").replace(",", ".")
    else:
        # si viene 1,234.56 (menos probable)
        t = t.replace(",", "")

    t = re.sub(r"[^\d\.\-]", "", t)
    try:
        return float(t)
    except Exception:
        return pd.NA


def clean_lista_reservas(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Excel 1 (LISTA RESERVAS):
    - localizador (clave)
    - fecha_alta
    - fecha_entrada / fecha_salida
    - ingresos (total reserva €)
    - alojamiento
    - origen_marketing
    """
    df = _normalize_columns(df_raw)

    # Mapeo robusto (por cómo lo has descrito)
    col_map = {}

    # claves típicas
    if "localizador" in df.columns:
        col_map["Localizador"] = "localizador"

    # fechas
    if "fecha_alta" in df.columns:
        col_map["Fecha_alta"] = "fecha_alta"
    elif "fechaalta" in df.columns:
        col_map["Fecha_alta"] = "fechaalta"

    if "fecha_entrada" in df.columns:
        col_map["Fecha_entrada"] = "fecha_entrada"
    elif "fechaentrada" in df.columns:
        col_map["Fecha_entrada"] = "fechaentrada"

    if "fecha_salida" in df.columns:
        col_map["Fecha_salida"] = "fecha_salida"
    elif "fechasalida" in df.columns:
        col_map["Fecha_salida"] = "fechasalida"

    # ingresos: "Total reserva (€)" suele normalizarse a total_reserva o total_reserva_e
    for cand in ("total_reserva", "total_reserva_e", "total_reserva_eur"):
        if cand in df.columns:
            col_map["Ingresos"] = cand
            break

    # alojamiento
    for cand in ("alojamiento", "nombre_alojamiento", "nombrealojamiento"):
        if cand in df.columns:
            col_map["Alojamiento"] = cand
            break

    # origen marketing
    for cand in ("origen_de_marketing", "origen_marketing", "origen_de_m", "origen"):
        if cand in df.columns:
            col_map["Origen_marketing"] = cand
            break

    # Validación mínima
    if "Localizador" not in col_map or "Ingresos" not in col_map:
        raise ValueError("❌ LISTA_RESERVAS: no encuentro 'Localizador' o 'Total reserva' (Ingresos).")

    out = pd.DataFrame()
    out["Localizador"] = df[col_map["Localizador"]].astype(str).str.strip()

    out["Fecha_alta"] = _to_datetime(df[col_map["Fecha_alta"]]) if "Fecha_alta" in col_map else pd.NaT
    out["Fecha_entrada"] = _to_datetime(df[col_map["Fecha_entrada"]]) if "Fecha_entrada" in col_map else pd.NaT
    out["Fecha_salida"] = _to_datetime(df[col_map["Fecha_salida"]]) if "Fecha_salida" in col_map else pd.NaT

    out["Ingresos"] = df[col_map["Ingresos"]].map(_to_number)

    out["Alojamiento"] = df[col_map["Alojamiento"]].map(_fix_mojibake) if "Alojamiento" in col_map else pd.NA
    out["Origen_marketing"] = df[col_map["Origen_marketing"]].map(_fix_mojibake) if "Origen_marketing" in col_map else pd.NA

    return out


def clean_listado_reservas(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Excel 2 (LISTADO RESERVAS / Avantio):
    Queremos marketing:
    - Localizador
    - Cliente país (cliente_pais)
    - Ocupante provincia (provincia)
    - Ocupante idioma (idioma)
    - Portal
    - Adultos/Ninos/Bebes
    - noches (si viene)
    """
    df = _normalize_columns(df_raw)

    if "localizador" not in df.columns:
        raise ValueError("❌ LISTADO_RESERVAS: no encuentro columna 'Localizador'.")

    out = pd.DataFrame()
    out["Localizador"] = df["localizador"].astype(str).str.strip()

    # País del cliente: "cliente_pais" suele venir como cliente_pais o cliente_pa_s (según mojibake)
    # con normalización se queda muy estable: cliente_pais
    if "cliente_pais" in df.columns:
        out["Pais"] = df["cliente_pais"].map(_fix_mojibake)
    else:
        out["Pais"] = pd.NA

    # Provincia del ocupante: ocupante_provincia
    if "ocupante_provincia" in df.columns:
        out["Provincia"] = df["ocupante_provincia"].map(_fix_mojibake)
    else:
        out["Provincia"] = pd.NA

    # Idioma del ocupante: ocupante_idioma_del_cliente
    # normalizado suele ser ocupante_idioma_del_cliente
    if "ocupante_idioma_del_cliente" in df.columns:
        out["Idioma"] = df["ocupante_idioma_del_cliente"].map(_fix_mojibake)
    elif "ocupante_idioma" in df.columns:
        out["Idioma"] = df["ocupante_idioma"].map(_fix_mojibake)
    else:
        out["Idioma"] = pd.NA

    # Portal
    out["Portal"] = df["portal"].map(_fix_mojibake) if "portal" in df.columns else pd.NA

    # Pax
    out["Adultos"] = pd.to_numeric(df["adultos"], errors="coerce") if "adultos" in df.columns else pd.NA
    out["Ninos"] = pd.to_numeric(df["ninos"], errors="coerce") if "ninos" in df.columns else pd.NA
    out["Bebes"] = pd.to_numeric(df["bebes"], errors="coerce") if "bebes" in df.columns else pd.NA

    # Noches si existe
    out["Noches"] = pd.to_numeric(df["noches"], errors="coerce") if "noches" in df.columns else pd.NA

    return out
