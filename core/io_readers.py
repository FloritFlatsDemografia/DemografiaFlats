import pandas as pd


def read_any(file):
    """
    Lee CSV/XLS/XLSX de Streamlit uploader.
    - CSV: intenta utf-8-sig y luego latin1 (por los PaÃ­s típicos).
    - Detecta separador automáticamente.
    """
    name = getattr(file, "name", "").lower()

    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)

    # CSV u otros: probar encodings típicos
    last_err = None
    for enc in ("utf-8-sig", "utf-8", "latin1"):
        try:
            return pd.read_csv(
                file,
                sep=None,
                engine="python",
                encoding=enc,
            )
        except Exception as e:
            last_err = e
            try:
                file.seek(0)
            except Exception:
                pass

    raise last_err
