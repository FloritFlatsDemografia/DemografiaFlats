import pandas as pd


def read_file(file) -> pd.DataFrame:
    name = file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(file, sep=None, engine="python")

    if name.endswith(".xls"):
        return pd.read_excel(file, engine="xlrd")

    if name.endswith(".xlsx"):
        return pd.read_excel(file, engine="openpyxl")

    raise ValueError("Formato no soportado")
