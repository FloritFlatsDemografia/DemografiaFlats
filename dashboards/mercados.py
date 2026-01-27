import streamlit as st
import plotly.express as px
import pandas as pd


def render_mercados(df: pd.DataFrame):
    st.subheader("Mercados (Marketing & Revenue)")

    # ───────── KPIs ─────────
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Reservas", f"{len(df):,}".replace(",", "."))
    c2.metric("Ingresos (€)", f"{df['ingreso'].sum():,.0f}".replace(",", "."))
    c3.metric("Noches", f"{df['noches'].sum():,.0f}".replace(",", "."))
    c4.metric("ADR (€)", f"{df['adr'].mean():.2f}")

    st.divider()

    # ───────── TOP PAÍS ─────────
    if "pais" in df:
        fig = px.bar(
            df.groupby("pais", as_index=False)
              .agg(reservas=("pais", "count"),
                   ingresos=("ingreso", "sum"))
              .sort_values("ingresos", ascending=False)
              .head(15),
            x="ingresos",
            y="pais",
            orientation="h",
            title="Ingresos por País"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ───────── PROVINCIA ─────────
    if "provincia" in df:
        fig = px.bar(
            df.groupby("provincia", as_index=False)
              .agg(ingresos=("ingreso", "sum"))
              .sort_values("ingresos", ascending=False)
              .head(15),
            x="ingresos",
            y="provincia",
            orientation="h",
            title="Ingresos por Provincia"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ───────── IDIOMA ─────────
    if "idioma" in df:
        fig = px.bar(
            df.groupby("idioma", as_index=False)
              .agg(adr=("adr", "mean"))
              .sort_values("adr", ascending=False)
              .head(15),
            x="adr",
            y="idioma",
            orientation="h",
            title="ADR por Idioma"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.caption("Datos limpios (post-procesado)")
    st.dataframe(df.head(200))
