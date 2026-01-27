import pandas as pd


def clean_listado_reservas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ─────────────────────────
    # NORMALIZAR NOMBRES
    # ─────────────────────────
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("€", "", regex=False)
        .str.replace("â‚¬", "", regex=False)
    )

    # ─────────────────────────
    # INGRESOS (columna M)
    # ─────────────────────────
    ingreso_candidates = [
        c for c in df.columns
        if "total_reserva" in c or "importe" in c or "ingreso" in c
    ]

    if ingreso_candidates:
        col_ingreso = ingreso_candidates[0]
        df["ingreso"] = (
            df[col_ingreso]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace("€", "", regex=False)
            .str.strip()
        )
        df["ingreso"] = pd.to_numeric(df["ingreso"], errors="coerce")
    else:
        df["ingreso"] = pd.NA

    # ─────────────────────────
    # FECHAS
    # ─────────────────────────
    for col in ["fecha_entrada", "fecha_salida"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # ─────────────────────────
    # NOCHES
    # ─────────────────────────
    if "fecha_entrada" in df.columns and "fecha_salida" in df.columns:
        df["noches"] = (df["fecha_salida"] - df["fecha_entrada"]).dt.days
    else:
        df["noches"] = pd.NA
