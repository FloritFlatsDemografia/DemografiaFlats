import pandas as pd
import unicodedata
import re


def _norm(s: str) -> str:
    """
    Normaliza texto para comparar nombres de columnas:
    - lower
    - sin tildes
    - sin símbolos raros
    - espacios colapsados
    """
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = s.replace("\ufeff", "")  # BOM invisible
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))  # quita tildes
    s = re.sub(r"[^a-z0-9\s:/_-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _find_col(df: pd.DataFrame, any_patterns) -> str | None:
    """
    Busca una columna cuyo nombre normalizado matchee ALGUNO de los patrones (regex sobre nombre normalizado).
    """
    cols = list(df.columns)
    norm_map = {c: _norm(c) for c in cols}

    for c, nc in norm_map.items():
        for pat in any_patterns:
            if re.search(pat, nc):
                return c
    return None


def _preview_cols(df: pd.DataFrame, n=40) -> str:
    cols = [str(c) for c in df.columns[:n]]
    if len(df.columns) > n:
        cols.append("...")
    return " | ".join(cols)


def clean_listado_reservas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1) Limpiar nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]

    # 2) Detectar fechas (MUY flexible)
    # Entrada: fecha + (entrada/entrac/entrad/check in/llegada/inicio)
    entrada_patterns = [
        r"\bfecha\b.*\bentr",          # "fecha entrac", "fecha entrada", "fecha entrad"
        r"\bentr\b.*\bfecha\b",
        r"\bcheck\s*in\b",
        r"\bllegada\b",
        r"\binicio\b.*\bestancia\b",
    ]

    # Salida: fecha + (salida/check out/fin)
    salida_patterns = [
        r"\bfecha\b.*\bsalid",
        r"\bsalid\b.*\bfecha\b",
        r"\bcheck\s*out\b",
        r"\bfin\b.*\bestancia\b",
    ]

    col_fecha_entrada = _find_col(df, entrada_patterns)
    col_fecha_salida = _find_col(df, salida_patterns)

    # 3) Ingresos: "total reserva", "importe", "total", "ingreso"
    ingresos_patterns = [
        r"\btotal\b.*\breserv",
        r"\bimporte\b",
        r"\btotal\b",
        r"\bingres",
    ]
    col_ingresos = _find_col(df, ingresos_patterns)

    # 4) Si sigue sin encontrar, intenta “plan B”: cualquier columna con "fecha" + otra con "salid/entr"
    if not col_fecha_entrada:
        col_fecha_entrada = _find_col(df, [r"\bfecha\b.*\bentr", r"\bfecha\b.*\bllegad", r"\bfecha\b.*\binici"])
    if not col_fecha_salida:
        col_fecha_salida = _find_col(df, [r"\bfecha\b.*\bsalid", r"\bfecha\b.*\bfin"])

    if not col_fecha_entrada or not col_fecha_salida:
        raise ValueError(
            "❌ No se han encontrado las columnas de Fecha entrada / salida.\n"
            "👉 Columnas detectadas (primeras):\n"
            f"{_preview_cols(df)}\n\n"
            "Solución rápida: revisa que existan columnas tipo 'Fecha entrada' y 'Fecha salida' "
            "(o 'Check-in' / 'Check-out')."
        )

    # 5) Crear columnas estándar
    df["Fecha entrada"] = pd.to_datetime(df[col_fecha_entrada], errors="coerce", dayfirst=True)
    df["Fecha salida"] = pd.to_datetime(df[col_fecha_salida], errors="coerce", dayfirst=True)

    # 6) Noches
    df["Noches"] = (df["Fecha salida"] - df["Fecha entrada"]).dt.days
    df["Noches"] = df["Noches"].fillna(0).clip(lower=0).astype(int)

    # 7) Ingresos
    if col_ingresos:
        df["Ingresos"] = pd.to_numeric(df[col_ingresos], errors="coerce")
    else:
        df["Ingresos"] = pd.NA

    # 8) ADR
    df["ADR"] = df["Ingresos"] / df["Noches"].replace({0: pd.NA})
    df["ADR"] = df["ADR"].fillna(0)

    # 9) Normalizar nombres comunes (País/Provincia/Idioma) si existen con variantes
    rename_map = {}
    for c in df.columns:
        nc = _norm(c)
        if re.search(r"\bpais\b", nc):
            rename_map[c] = "País"
        elif re.search(r"\bprovincia\b", nc):
            rename_map[c] = "Provincia"
        elif re.search(r"\bidioma\b", nc) or re.search(r"\blanguage\b", nc):
            rename_map[c] = "Idioma"
        elif re.search(r"\bportal\b", nc) or re.search(r"\bcanal\b", nc) or re.search(r"\borigen\b", nc):
            rename_map[c] = "Portal"

    df = df.rename(columns=rename_map)

    return df
