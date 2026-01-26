import pandas as pd
from core.schema import ColumnMap

def build_dataset(df_lista: pd.DataFrame, df_listado: pd.DataFrame, cm: ColumnMap) -> pd.DataFrame:
    # Unimos todo lo que podamos; para este paso inicial, simplemente concatenamos
    data = pd.concat([df_lista, df_listado], ignore_index=True, sort=False)

    out = pd.DataFrame()

    if cm.pais and cm.pais in data.columns:
        out["País"] = data[cm.pais].astype(str).str.strip()
    else:
        out["País"] = ""

    if cm.provincia and cm.provincia in data.columns:
        out["Provincia"] = data[cm.provincia].astype(str).str.strip()
    else:
        out["Provincia"] = ""

    if cm.idioma and cm.idioma in data.columns:
        out["Idioma"] = data[cm.idioma].astype(str).str.strip()
    else:
        out["Idioma"] = ""

    if cm.portal and cm.portal in data.columns:
        out["Portal"] = data[cm.portal].astype(str).str.strip()
    else:
        out["Portal"] = ""

    # Limpieza de valores vacíos típicos
    for c in ["País", "Provincia", "Idioma", "Portal"]:
        out[c] = out[c].replace(["nan", "None", "NaT", ""], "").fillna("")

    return out
