import pandas as pd


def _read_csv_robust(file) -> pd.DataFrame:
    """
    Lee CSV con múltiples encodings y separadores (sin que explote en Streamlit Cloud).
    """
    # Streamlit uploader puede volver a usarse varias veces: reseteamos puntero
    try:
        file.seek(0)
    except Exception:
        pass

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
    last_err = None

    for enc in encodings:
        try:
            file.seek(0)
            # sep=None + engine python intenta autodetectar delimitador
            return pd.read_csv(file, sep=None, engine="python", encoding=enc)
        except Exception as e:
            last_err = e

    raise last_err


def _read_excel_robust(file) -> pd.DataFrame:
    try:
        file.seek(0)
    except Exception:
        pass
    return pd.read_excel(file, engine="openpyxl")


def read_any(file) -> pd.DataFrame:
    """
    Acepta CSV / XLS / XLSX. Devuelve DataFrame.
    """
    name = (getattr(file, "name", "") or "").lower()
    if name.endswith(".csv"):
        return _read_csv_robust(file)
    if name.endswith(".xls") or name.endswith(".xlsx"):
        return _read_excel_robust(file)

    # fallback: intenta CSV
    return _read_csv_robust(file)
