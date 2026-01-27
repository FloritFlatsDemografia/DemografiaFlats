import pandas as pd


def read_any(file):
    name = file.name.lower()

    if name.endswith(".csv"):
        try:
            return pd.read_csv(file, sep=None, engine="python")
        except UnicodeDecodeError:
            return pd.read_csv(file, sep=None, engine="python", encoding="latin1")

    if name.endswith((".xls", ".xlsx")):
        return pd.read_excel(file)

    raise ValueError("Formato de archivo no soportado")
