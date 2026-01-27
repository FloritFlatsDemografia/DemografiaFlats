import pandas as pd
import streamlit as st
import plotly.express as px


def _top_count(df: pd.DataFrame, col: str, n=15) -> pd.DataFrame:
    if col not in df.columns:
        return pd.DataFrame({col: [], "Reservas": []})
    s = df[col].replace("", pd.NA).dropna()
    if s.empty:
        return pd.DataFrame({col: [], "Reservas": []})
    t = s.value_counts().head(n).reset_index()
    t.columns = [col, "Reservas"]
    return t


def _top_sum(df: pd.DataFrame, group_col: str, value_col: str, n=15) -> pd.DataFrame:
    if group_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame({group_col: [], value_col: []})
    x = df[[group_col, value_col]].dropna()
    if x.empty:
        return pd.DataFrame({group_col: [], value_col: []})
    t = x.groupby(group_col, as_index=False)[value_col].sum().sort_values(value_col, ascending=False).head(n)
    return t


def render_mercados(df: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    # KPIs
    reservas = len(df)
    ingresos = pd.to_numeric(df["Ingreso"], errors="coerce").sum() if "Ingreso" in df.columns else None
    noches = pd.to_numeric(df["Noches"], errors="coerce").sum() if "Noches" in df.columns else None
    adr = (ingresos / noches) if (ingresos is not None and noches and noches > 0) else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reservas", f"{reservas:,}".replace(",", "."))
    c2.metric("Ingresos", f"{ingresos:,.0f} €".replace(",", "X").replace(".", ",").replace("X", ".") if ingresos is not None else "—")
    c3.metric("Noches", f"{noches:,.0f}".replace(",", ".") if noches is not None else "—")
    c4.metric("ADR", f"{adr:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".") if adr is not None else "—")

    st.divider()

    # Gráficos: Reservas
    g1, g2, g3 = st.columns(3)

    with g1:
        st.caption("Top País (Reservas)")
        tp = _top_count(df, "País", 15)
        if tp.empty:
            st.info("No hay datos de País.")
        else:
            st.plotly_chart(px.bar(tp, x="Reservas", y="País", orientation="h"), use_container_width=True)

    with g2:
        st.caption("Top Provincia (Reservas)")
        tv = _top_count(df, "Provincia", 15)
        if tv.empty:
            st.info("No hay datos de Provincia.")
        else:
            st.plotly_chart(px.bar(tv, x="Reservas", y="Provincia", orientation="h"), use_container_width=True)

    with g3:
        st.caption("Top Idioma (Reservas)")
        ti = _top_count(df, "Idioma", 15)
        if ti.empty:
            st.info("No hay datos de Idioma.")
        else:
            st.plotly_chart(px.bar(ti, x="Reservas", y="Idioma", orientation="h"), use_container_width=True)

    st.divider()

    # Gráficos: Dinero
    h1, h2 = st.columns(2)

    with h1:
        st.caption("Top País (Ingresos)")
        ts = _top_sum(df, "País", "Ingreso", 15)
        if ts.empty:
            st.info("No hay ingresos por País.")
        else:
            st.plotly_chart(px.bar(ts, x="Ingreso", y="País", orientation="h"), use_container_width=True)

    with h2:
        st.caption("Ingresos por Portal")
        tp2 = _top_sum(df, "Portal", "Ingreso", 12)
        if tp2.empty:
            st.info("No hay ingresos por Portal.")
        else:
            st.plotly_chart(px.bar(tp2, x="Ingreso", y="Portal", orientation="h"), use_container_width=True)

    st.divider()
    st.caption("Muestra de datos (post-filtro)")
    st.dataframe(df.head(300), use_container_width=True)
