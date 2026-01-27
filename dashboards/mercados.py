import streamlit as st
import pandas as pd
import plotly.express as px


def _top_counts(df: pd.DataFrame, col: str, n=15) -> pd.DataFrame:
    s = df[col].dropna().astype(str).str.strip()
    if s.empty:
        return pd.DataFrame({col: [], "Reservas": []})
    t = s.value_counts().head(n).reset_index()
    t.columns = [col, "Reservas"]
    return t


def _top_sum(df: pd.DataFrame, col: str, value_col: str, n=15) -> pd.DataFrame:
    d = df[[col, value_col]].dropna()
    if d.empty:
        return pd.DataFrame({col: [], "Ingresos": []})
    d[col] = d[col].astype(str).str.strip()
    t = d.groupby(col, as_index=False)[value_col].sum().sort_values(value_col, ascending=False).head(n)
    t = t.rename(columns={value_col: "Ingresos"})
    return t


def _top_adr(df: pd.DataFrame, col: str, n=15) -> pd.DataFrame:
    d = df[[col, "ADR"]].dropna()
    if d.empty:
        return pd.DataFrame({col: [], "ADR": []})
    d[col] = d[col].astype(str).str.strip()
    t = d.groupby(col, as_index=False)["ADR"].mean().sort_values("ADR", ascending=False).head(n)
    return t


def render_mercados(df: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    # KPIs
    reservas = len(df)
    ingresos = df["Ingresos"].sum(skipna=True) if "Ingresos" in df.columns else 0
    noches = df["Noches"].sum(skipna=True) if "Noches" in df.columns else 0
    adr = (ingresos / noches) if noches and noches > 0 else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reservas", f"{reservas:,}".replace(",", "."))
    c2.metric("Ingresos", f"{ingresos:,.0f} €".replace(",", "X").replace(".", ",").replace("X", ".") if ingresos else "—")
    c3.metric("Noches", f"{int(noches):,}".replace(",", ".") if noches else "—")
    c4.metric("ADR", f"{adr:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".") if adr else "—")

    st.divider()

    # Selector de métrica (marketing + dinero)
    metric = st.radio(
        "¿Qué quieres ver?",
        ["Reservas", "Ingresos", "ADR"],
        horizontal=True
    )

    dims = [
        ("Pais", "País (Cliente)"),
        ("Provincia", "Provincia (Ocupante)"),
        ("Idioma", "Idioma (Cliente)"),
        ("Portal", "Portal"),
        ("Origen_marketing", "Origen de marketing"),
        ("Alojamiento", "Alojamiento"),
    ]

    cols = st.columns(3)
    for i, (col, label) in enumerate(dims[:3]):
        with cols[i]:
            st.caption(f"Top {label} ({metric})")
            if metric == "Reservas":
                t = _top_counts(df, col, 15)
                fig = px.bar(t, x="Reservas", y=col, orientation="h")
            elif metric == "Ingresos":
                t = _top_sum(df, col, "Ingresos", 15)
                fig = px.bar(t, x="Ingresos", y=col, orientation="h")
            else:
                t = _top_adr(df, col, 15)
                fig = px.bar(t, x="ADR", y=col, orientation="h")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    cols2 = st.columns(3)
    for i, (col, label) in enumerate(dims[3:6]):
        with cols2[i]:
            st.caption(f"Top {label} ({metric})")
            if metric == "Reservas":
                t = _top_counts(df, col, 15)
                fig = px.bar(t, x="Reservas", y=col, orientation="h")
            elif metric == "Ingresos":
                t = _top_sum(df, col, "Ingresos", 15)
                fig = px.bar(t, x="Ingresos", y=col, orientation="h")
            else:
                t = _top_adr(df, col, 15)
                fig = px.bar(t, x="ADR", y=col, orientation="h")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Extra marketing MUY útil: Lead time (cuándo reserva la gente)
    st.caption("Lead time (días entre reserva y entrada) — útil para planificar campañas")
    if "Lead_time_dias" in df.columns and df["Lead_time_dias"].dropna().shape[0] > 0:
        lt = df["Lead_time_dias"].dropna()
        fig = px.histogram(lt, nbins=40)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay lead time disponible (faltan fechas de alta o entrada en LISTA_RESERVAS).")

    st.divider()
    st.caption("Muestra de datos (post-proceso)")
    st.dataframe(df.head(200), use_container_width=True)
