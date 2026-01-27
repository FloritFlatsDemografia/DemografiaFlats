import streamlit as st

from core.pipeline import load_and_prepare
from core.filters import apply_filters
from dashboards.mercados import render_mercados

st.set_page_config(page_title="Florit - Marketing Intelligence", layout="wide")

st.title("Florit - Marketing Intelligence")

st.sidebar.header("Subida de archivos")

f_lista = st.sidebar.file_uploader(
    "LISTA_RESERVAS (CSV / XLS / XLSX)",
    type=["csv", "xls", "xlsx"],
    key="lista",
)

f_listado = st.sidebar.file_uploader(
    "LISTADO_RESERVAS (CSV / XLS / XLSX)",
    type=["csv", "xls", "xlsx"],
    key="listado",
)

if not f_lista or not f_listado:
    st.info("⬅️ Sube los 2 archivos para comenzar: **Lista reservas** y **Listado de reservas**.")
    st.stop()

try:
    df = load_and_prepare(f_lista, f_listado)
except Exception as e:
    st.error("Error preparando los datos.")
    st.exception(e)
    st.stop()

df_f = apply_filters(df)

render_mercados(df_f)
