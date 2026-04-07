import streamlit as st

from core.pipeline import load_and_prepare
from core.filters import apply_filters
from dashboards.mercados import render_mercados


st.set_page_config(page_title="Florit - Marketing Intelligence", layout="wide")

st.title("Florit - Marketing Intelligence")

st.sidebar.header("Subida de archivos")

f_lista = st.sidebar.file_uploader(
    "LISTA_RESERVAS (CSV/XLS/XLSX)",
    type=["csv", "xls", "xlsx"],
    key="lista",
)

f_listado = st.sidebar.file_uploader(
    "LISTADO_RESERVAS (CSV/XLS/XLSX)",
    type=["csv", "xls", "xlsx"],
    key="listado",
)

if not f_lista or not f_listado:
    st.info("⬅️ Sube los **2 archivos** para comenzar: LISTA_RESERVAS y LISTADO_RESERVAS.")
    st.stop()

try:
    # validación básica de extensiones
    ext_lista = f_lista.name.lower().split(".")[-1]
    ext_listado = f_listado.name.lower().split(".")[-1]

    extensiones_validas = {"csv", "xls", "xlsx"}

    if ext_lista not in extensiones_validas:
        st.error(f"El archivo LISTA_RESERVAS no tiene un formato válido: {f_lista.name}")
        st.stop()

    if ext_listado not in extensiones_validas:
        st.error(f"El archivo LISTADO_RESERVAS no tiene un formato válido: {f_listado.name}")
        st.stop()

    # mensaje preventivo para .xls
    if ext_lista == "xls" or ext_listado == "xls":
        st.warning(
            "Has subido un archivo .xls. Para este formato debes tener instalada la librería "
            "'xlrd>=2.0.1'. Si falla, guarda el archivo como .xlsx y vuelve a subirlo."
        )

    df = load_and_prepare(f_lista, f_listado)

except ImportError as e:
    mensaje = str(e).lower()

    if "xlrd" in mensaje:
        st.error(
            "Error procesando archivos: falta la librería 'xlrd' para leer archivos .xls. "
            "Instálala en requirements.txt o convierte el archivo a .xlsx."
        )
    elif "openpyxl" in mensaje:
        st.error(
            "Error procesando archivos: falta la librería 'openpyxl' para leer archivos .xlsx. "
            "Instálala en requirements.txt."
        )
    else:
        st.error(f"Error de importación al procesar archivos: {e}")

    st.stop()

except Exception as e:
    st.error(f"Error procesando archivos: {e}")
    st.stop()

# filtros marketing
df_f = apply_filters(df)

# dashboard marketing
render_mercados(df_f)
