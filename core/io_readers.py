import pandas as pd


def read_any(file):
    """
    Lee CSV/XLS/XLSX desde Streamlit uploader.
    - CSV: intenta varios encodings y detecta separador
    - Excel: read_excel
    """
    name = (getattr(file, "name", "") or "").lower()

    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)

    # CSV / TXT
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    last_err = None
    for enc in encodings:
        try:
            return pd.read_csv(file, sep=None, engine="python", encoding=enc)
        except Exception as e:
            last_err = e
            try:
                file.seek(0)
            except Exception:
                pass

    raise last_err
