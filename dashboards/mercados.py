import streamlit as st
import plotly.express as px
import pandas as pd


def _top(df, col, value_col=None, n=10):
    if value_col:
        return (
            df.groupby(col)[value_col]
            .sum()
            .sort_values(ascending=False)
            .head(n)
            .reset_index()
        )
    else:
        return (
            df[col]
            .value_counts()
            .head(n)
            .reset_index()
            .rename(columns={"index": col, col: "Reservas"})
        )


def render_mercados(df: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Reservas", f"{len(df):,}".replace(",", "."))

    with c2:
        total_ingresos = df["Ingresos"].sum()
        st.metric("Ingresos", f"{total_ingresos:,.0f} €".replace(",", "."))

    with c3:
        noches = df["Noches"].sum()
        st.metric("Noches", f"{noches:,.0f}".replace(",", "."))

    with c4:
        adr = total_ingresos / noches if noches > 0 else 0
        st.metric("ADR", f"{adr:,.2f} €".replace(",", "."))

    st.divider()

    g1, g2, g3 = st.columns(3)

    with g1:
        st.caption("Top País (Reservas)")
        tp = _top(df, "País")
        st.plotly_chart(px.bar(tp, x="Reservas", y="País", orientation="h"), use_container_width=True)

    with g2:
        st.caption("Top Provincia (Reservas)")
        tv = _top(df, "Provincia")
        st.plotly_chart(px.bar(tv, x="Reservas", y="Provincia", orientation="h"), use_container_width=True)

    with g3:
        st.caption("Top Idioma (Reservas)")
        ti = _top(df, "Idioma")
        st.plotly_chart(px.bar(ti, x="Reservas", y="Idioma", orientation="h"), use_container_width=True)

    st.divider()

    st.caption("Muestra de datos")
    st.dataframe(df.head(200))
