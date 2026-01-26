import streamlit as st
import pandas as pd
import plotly.express as px

def _top(df: pd.DataFrame, col: str, n=15) -> pd.DataFrame:
    s = df[col].replace("", pd.NA).dropna()
    if s.empty:
        return pd.DataFrame({col: [], "Reservas": []})
    t = s.value_counts().head(n).reset_index()
    t.columns = [col, "Reservas"]
    return t

def render_mercados(d: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("Top País")
        tp = _top(d, "País", 15)
        st.plotly_chart(px.bar(tp, x="Reservas", y="País", orientation="h"), use_container_width=True)

    with c2:
        st.caption("Top Provincia")
        tv = _top(d, "Provincia", 15)
        st.plotly_chart(px.bar(tv, x="Reservas", y="Provincia", orientation="h"), use_container_width=True)

    with c3:
        st.caption("Top Idioma")
        ti = _top(d, "Idioma", 15)
        st.plotly_chart(px.bar(ti, x="Reservas", y="Idioma", orientation="h"), use_container_width=True)

    st.divider()
    st.caption("Muestra de datos (post-filtro)")
    st.dataframe(d.head(200))

