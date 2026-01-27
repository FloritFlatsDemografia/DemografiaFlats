import streamlit as st
from core.pipeline import load_and_prepare
from dashboards.mercados import render_mercados

st.set_page_config(layout="wide")

st.title("Florit - Marketing Intelligence")

st.sidebar.header("Subida de archivos")

f_lista = st.sidebar.file_uploader(
    "LISTA_RESERVAS (CSV / XLS / XLSX)",
    type=["csv", "xls", "xlsx"]
)

f_listado = st.sidebar.file_uploader(
    "LISTADO_RESERVAS (CSV / XLS / XLSX)",
    type=["csv", "xls", "xlsx"]
)

if not f_lista or not f_listado:
    st.info("⬅️ Sube los dos archivos para comenzar")
    st.stop()

df = load_and_prepare(f_lista, f_listado)

render_mercados(df)
