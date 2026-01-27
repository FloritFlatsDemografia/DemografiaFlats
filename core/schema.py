from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class ColumnMap:
    pais: str | None
    provincia: str | None
    idioma: str | None
    portal: str | None

def _find_col(cols, candidates):
    cols_l = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_l:
            return cols_l[cand.lower()]
    return None

def detect_columns(df_lista: pd.DataFrame, df_listado: pd.DataFrame) -> ColumnMap:
    cols = list(df_lista.columns) + list(df_listado.columns)

    pais = _find_col(cols, [
        "Ocupante: País", "Ocupante: PaÃ­s", "Pais", "País", "Country"
    ])
    provincia = _find_col(cols, [
        "Ocupante: Provincia", "Provincia", "Province"
    ])
    idioma = _find_col(cols, [
        "Ocupante: Idioma del cliente", "Idioma del cliente", "Idioma", "Language"
    ])
    portal = _find_col(cols, [
        "Portal", "Web origen", "Origen", "Channel"
    ])

    return ColumnMap(pais=pais, provincia=provincia, idioma=idioma, portal=portal)
