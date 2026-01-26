import streamlit as st
import pandas as pd

def sidebar_filters(d: pd.DataFrame) -> dict:
    st.sidebar.header("Filtros")

    paises = sorted([x for x in d["País"].unique().tolist() if x])
    provincias = sorted([x for x in d["Provincia"].unique().tolist() if x])
    idiomas = sorted([x for x in d["Idioma"].unique().tolist() if x])
    portales = sorted([x for x in d["Portal"].unique().tolist() if x])

    f = {}
    f["pais"] = st.sidebar.multiselect("País", paises)
    f["provincia"] = st.sidebar.multiselect("Provincia", provincias)
    f["idioma"] = st.sidebar.multiselect("Idioma", idiomas)
    f["portal"] = st.sidebar.multiselect("Portal", portales)
    return f

def apply_filters(d: pd.DataFrame, f: dict) -> pd.DataFrame:
    out = d.copy()
    if f.get("pais"):
        out = out[out["País"].isin(f["pais"])]
    if f.get("provincia"):
        out = out[out["Provincia"].isin(f["provincia"])]
    if f.get("idioma"):
        out = out[out["Idioma"].isin(f["idioma"])]
    if f.get("portal"):
        out = out[out["Portal"].isin(f["portal"])]
    return out
