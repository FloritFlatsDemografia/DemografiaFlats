from __future__ import annotations

import pandas as pd
import unicodedata
import re


# -----------------------
# Utilidades
# -----------------------
def _norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower().replace("\ufeff", "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s:/_-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _fix_mojibake(x: str) -> str:
    """
    Arregla casos tipo 'EspaÃ±a' -> 'España' si viene por CSV mal decodificado.
    Si no aplica, devuelve igual.
    """
    if not isinstance(x, str):
        return x
    if "Ã" in x or "Â" in x:
        try:
            return x.encode("latin1").decode("utf-8")
        except Exception:
            return x
    return x


def _find_col_by_name(df: pd.DataFrame, patterns: list[str]) -> str | None:
    for c in df.columns:
        nc = _norm(c)
        for pat in patterns:
            if re.search(pat, nc):
                return c
    return None


def _date_like_score(series: pd.Series) -> int:
    s = pd.to_datetime(series, errors="coerce", dayfirst=True)
    return int(s.notna().sum())


def _pick_date_columns_by_content(df: pd.DataFrame) -> tuple[str | None, str | None]:
    # Evalúa todas las columnas y se queda con las 2 más "date-like"
    scores = []
    for c in df.columns:
        try:
            score = _date_like_score(df[c])
        except Exception:
            score = 0
        scores.append((score, c))

    scores.sort(reverse=True, key=lambda x: x[0])
    if not scores or scores[0][0] == 0:
        return None, None

    c1 = scores[0][1]
    c2 = None
    for score, c in scores[1:]:
        if c != c1 and score > 0:
            c2 = c
            break

    if not c2:
        return c1, None

    # Decide cuál es entrada/salida por mediana: entrada suele ser menor
    d1 = pd.to_datetime(df[c1], errors="coerce", dayfirst=True)
    d2 = pd.to_datetime(df[c2], errors="coerce", dayfirst=True)

    m1 = d1.dropna().median() if d1.notna().any() else None
    m2 = d2.dropna().median() if d2.notna().any() else None

    if m1 is not None and m2 is not None:
        if m1 <= m2:
            return c1, c2
        return c2, c1

    # fallback: por nombre
    if re.search(r"\bentr", _norm(c1)) or re.search(r"\bcheck in\b", _norm(c1)):
        return c1, c2
    if re.search(r"\bsalid|\bcheck out\b", _norm(c1)):
        return c2, c1

    return c1, c2


def _pick_income_column(df: pd.DataFrame) -> str | None:
    # 1) Por nombre (preferencias típicas)
    name_patterns = [
        r"\btotal\b.*\breserv",
        r"\bimporte\b",
        r"\btotal\b",
        r"\bingres",
        r"\bprecio\b",
    ]
    c = _find_col_by_name(df, name_patterns)
    if c:
        return c

    # 2) Por contenido: columna numérica con mayor suma positiva
    best = None
    best_score = None
    for c in df.columns:
        try:
            s = pd.to_numeric(df[c], errors="coerce")
            score = float(s.fillna(0).clip(lower=0).sum())
            nonnull = int(s.notna().sum())
            # penaliza si casi todo es NaN
            if nonnull < max(10, int(len(df) * 0.05)):
                continue
            if best_score is None or score > best_score:
                best_score = score
                best = c
        except Exception:
            continue
    return best


# -----------------------
# Cleaners principales
# -----------------------
def clean_lista_reservas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Archivo 'LISTA_RESERVAS': suele traer País/Provincia/Idioma/Portal, etc.
    Normalizamos texto y arreglamos mojibake.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Arregla texto en columnas object
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].map(_fix_mojibake)

    # Renombra variantes conocidas si aparecen
    rename_map = {}
    for c in df.columns:
        nc = _norm(c)
        if re.search(r"\bpais\b", nc):
            rename_map[c] = "País"
        elif re.search(r"\bprovincia\b", nc):
            rename_map[c] = "Provincia"
        elif re.search(r"\bidioma\b|\blanguage\b", nc):
            rename_map[c] = "Idioma"
        elif re.search(r"\bportal\b|\bcanal\b|\borigen\b", nc):
            rename_map[c] = "Portal"

    df = df.rename(columns=rename_map)
    return df


def clean_listado_reservas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Archivo 'LISTADO_RESERVAS': aquí sacamos Fecha entrada/salida, Noches, Ingresos, ADR.
    - No depende SOLO de nombres: si hace falta, detecta por CONTENIDO.
    - Nunca revienta la app: si no puede, deja NaT/0 y sigue.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Arregla mojibake en texto
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].map(_fix_mojibake)

    # 1) Intento por nombre
    entrada_patterns = [r"\bfecha\b.*\bentr", r"\bcheck\s*in\b", r"\bllegada\b", r"\binicio\b"]
    salida_patterns = [r"\bfecha\b.*\bsalid", r"\bcheck\s*out\b", r"\bfin\b"]

    col_in = _find_col_by_name(df, entrada_patterns)
    col_out = _find_col_by_name(df, salida_patterns)

    # 2) Si falta algo, intento por contenido
    if not col_in or not col_out:
        cin2, cout2 = _pick_date_columns_by_content(df)
        col_in = col_in or cin2
        col_out = col_out or cout2

    # 3) Fechas
    df["Fecha entrada"] = pd.to_datetime(df[col_in], errors="coerce", dayfirst=True) if col_in else pd.NaT
    df["Fecha salida"] = pd.to_datetime(df[col_out], errors="coerce", dayfirst=True) if col_out else pd.NaT

    # 4) Noches
    if col_in and col_out:
        df["Noches"] = (df["Fecha salida"] - df["Fecha entrada"]).dt.days
        df["Noches"] = df["Noches"].fillna(0).clip(lower=0).astype(int)
    else:
        df["Noches"] = 0

    # 5) Ingresos
    col_income = _pick_income_column(df)
    df["Ingresos"] = pd.to_numeric(df[col_income], errors="coerce") if col_income else pd.NA

    # 6) ADR
    df["ADR"] = df["Ingresos"] / df["Noches"].replace({0: pd.NA})
    df["ADR"] = df["ADR"].fillna(0)

    # 7) Normalizar País/Provincia/Idioma/Portal si existen
    rename_map = {}
    for c in df.columns:
        nc = _norm(c)
        if c in ["País", "Provincia", "Idioma", "Portal"]:
            continue
        if re.search(r"\bpais\b", nc):
            rename_map[c] = "País"
        elif re.search(r"\bprovincia\b", nc):
            rename_map[c] = "Provincia"
        elif re.search(r"\bidioma\b|\blanguage\b", nc):
            rename_map[c] = "Idioma"
        elif re.search(r"\bportal\b|\bcanal\b|\borigen\b", nc):
            rename_map[c] = "Portal"

    df = df.rename(columns=rename_map)

    return df
