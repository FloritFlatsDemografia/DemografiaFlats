import pandas as pd
import streamlit as st


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    st.sidebar.subheader("Filtros")

    # Fecha
    if "Fecha entrada" in d.columns and pd.api.types.is_datetime64_any_dtype(d["Fecha entrada"]):
        min_dt = d["Fecha entrada"].min()
        max_dt = d["Fecha entrada"].max()
        if pd.notna(min_dt) and pd.notna(max_dt):
            start, end = st.sidebar.date_input(
                "Rango de fechas (Fecha entrada)",
                value=(min_dt.date(), max_dt.date()),
            )
            d = d[(d["Fecha entrada"].dt.date >= start) & (d["Fecha entrada"].dt.date <= end)]

    def multiselect(col: str, label: str):
        if col in d.columns:
            opts = sorted([x for x in d[col].dropna().unique().tolist() if str(x).strip() != ""])
            sel = st.sidebar.multiselect(label, opts)
            if sel:
                return d[d[col].isin(sel)]
        return d

    d = multiselect("País", "País")
    d = multiselect("Provincia", "Provincia")
    d = multiselect("Idioma", "Idioma")
    d = multiselect("Portal", "Portal")
    d = multiselect("Alojamiento", "Alojamiento")

    return d
