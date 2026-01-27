import streamlit as st
import pandas as pd


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtros marketing (Pais/Provincia/Idioma/Portal).
    """
    st.sidebar.header("Filtros")

    def _multiselect(label, col):
        if col not in df.columns:
            return []
        opts = sorted([x for x in df[col].dropna().unique().tolist() if str(x).strip() != ""])
        return st.sidebar.multiselect(label, opts)

    sel_pais = _multiselect("País", "Pais")
    sel_prov = _multiselect("Provincia", "Provincia")
    sel_idioma = _multiselect("Idioma", "Idioma")
    sel_portal = _multiselect("Portal", "Portal")

    out = df.copy()
    if sel_pais:
        out = out[out["Pais"].isin(sel_pais)]
    if sel_prov:
        out = out[out["Provincia"].isin(sel_prov)]
    if sel_idioma:
        out = out[out["Idioma"].isin(sel_idioma)]
    if sel_portal:
        out = out[out["Portal"].isin(sel_portal)]

    return out
