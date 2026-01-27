import streamlit as st
from core.pipeline import load_and_prepare
from dashboards.mercados import render_mercados

st.set_page_config(layout="wide")
st.title("Florit - Marketing Intelligence")

st.sidebar.header("Subida de archivos")

f_lista = st.sidebar.file_uploader(
    "LISTA_RESERVAS (ingresos)",
    type=["csv", "xls", "xlsx"]
)

f_listado = st.sidebar.file_uploader(
    "LISTADO_RESERVAS (perfil cliente)",
    type=["csv", "xls", "xlsx"]
)

if not f_lista or not f_listado:
    st.info("⬅️ Sube los DOS archivos para comenzar")
    st.stop()

df = load_and_prepare(f_lista, f_listado)

# ─────────── FILTROS ───────────
st.sidebar.header("Filtros")

def multi(col):
    return st.sidebar.multiselect(
        col,
        sorted(df[col].dropna().unique())
    ) if col in df.columns else []

f_pais = multi("País")
f_prov = multi("Provincia")
f_idioma = multi("Idioma")
f_portal = multi("Portal")

df_f = df.copy()

if f_pais:
    df_f = df_f[df_f["País"].isin(f_pais)]
if f_prov:
    df_f = df_f[df_f["Provincia"].isin(f_prov)]
if f_idioma:
    df_f = df_f[df_f["Idioma"].isin(f_idioma)]
if f_portal:
    df_f = df_f[df_f["Portal"].isin(f_portal)]

render_mercados(df_f)
