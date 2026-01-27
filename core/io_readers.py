import pandas as pd
import io


def read_any(file) -> pd.DataFrame:
    name = file.name.lower()

    # ───────── CSV ─────────
    if name.endswith(".csv"):
        raw = file.read()
        file.seek(0)

        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                return pd.read_csv(
                    io.BytesIO(raw),
                    encoding=enc,
                    sep=None,
                    engine="python"
                )
            except Exception:
                continue

        raise ValueError("No se pudo leer el CSV con ninguna codificación conocida")

    # ───────── EXCEL ─────────
    if name.endswith(".xlsx"):
        return pd.read_excel(file, engine="openpyxl")

    if name.endswith(".xls"):
        return pd.read_excel(file, engine="xlrd")

    raise ValueError("Formato de archivo no soportado")
