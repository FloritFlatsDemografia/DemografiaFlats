from __future__ import annotations

import io
import csv
import pandas as pd


def _get_bytes(file) -> bytes:
    # Streamlit UploadedFile tiene getvalue()
    if hasattr(file, "getvalue"):
        return file.getvalue()
    # fallback
    data = file.read()
    return data if isinstance(data, (bytes, bytearray)) else str(data).encode("utf-8", errors="ignore")


def _guess_delimiter(sample: str) -> str:
    # Heurística rápida
    counts = {
        ";": sample.count(";"),
        ",": sample.count(","),
        "\t": sample.count("\t"),
        "|": sample.count("|"),
    }
    delim = max(counts, key=counts.get)
    # Si todo 0, intenta sniffer
    if counts[delim] == 0:
        try:
            dialect = csv.Sniffer().sniff(sample)
            return dialect.delimiter
        except Exception:
            return ","
    return delim


def read_any(file) -> pd.DataFrame:
    """
    Lee CSV/XLS/XLSX desde Streamlit UploadedFile con máxima robustez.
    """
    name = getattr(file, "name", "") or ""
    low = name.lower()

    # Excel
    if low.endswith(".xlsx") or low.endswith(".xls"):
        return pd.read_excel(file)

    # CSV / texto
    raw = _get_bytes(file)

    # Intentos de encoding
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    last_err = None

    for enc in encodings:
        try:
            text = raw.decode(enc)
            # muestra inicial para delim
            sample = "\n".join(text.splitlines()[:20])
            delim = _guess_delimiter(sample)

            # read_csv desde StringIO
            return pd.read_csv(
                io.StringIO(text),
                sep=delim,
                engine="python",
            )
        except Exception as e:
            last_err = e
            continue

    # Último intento: pandas con sep auto (puede fallar, pero por lo menos lo intenta)
    try:
        return pd.read_csv(io.BytesIO(raw), sep=None, engine="python", encoding_errors="ignore")
    except Exception:
        raise last_err if last_err else RuntimeError("No se pudo leer el archivo.")
