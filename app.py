import streamlit as st
from core.pipeline import load_and_prepare
from core.filters import sidebar_filters, apply_filters

from dashboards.mercados import render_mercados

st.set_page_config(page_title="Florit - Marketing Intelligence", layout="wide")
st.title("Florit - Marketing Intelligence")

with st.sidebar:
    st.header("Subida de archivos")
    f_lista = st.file_uploader("LISTA_RESERVAS (CSV/XLS/XLSX)", type=["csv","xls","xlsx"])
    f_listado = st.file_uploader("LISTADO_RESERVAS (CSV/XLS/XLSX)", type=["csv","xls","xlsx"])

if not f_lista or not f_listado:
    st.info("Sube los dos archivos para empezar.")
    st.stop()

df_lista, df_listado, cm, data = load_and_prepare(f_lista, f_listado)

filters = sidebar_filters(data)
d = apply_filters(data, filters)

render_mercados(d)
