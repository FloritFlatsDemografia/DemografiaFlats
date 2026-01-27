import streamlit as st
from core.io_readers import read_file
from core.cleaning import clean_cols
from core.schema import detect_columns
from core.dataset import build_dataset

@st.cache_data(show_spinner=True)
def load_and_prepare(f_lista, f_listado):
    df_lista = clean_cols(read_file(f_lista))
    df_listado = clean_cols(read_file(f_listado))
    cm = detect_columns(df_lista, df_listado)
    data = build_dataset(df_lista, df_listado, cm)
    return df_lista, df_listado, cm, data
