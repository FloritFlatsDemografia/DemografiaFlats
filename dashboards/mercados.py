import streamlit as st
import pandas as pd
import plotly.express as px


def _kpi_row(df: pd.DataFrame):
    reservas = int(df["Localizador"].nunique()) if "Localizador" in df.columns else len(df)
    ingresos = df["Ingresos"].sum(skipna=True) if "Ingresos" in df.columns else 0.0
    noches = df["Noches"].sum(skipna=True) if "Noches" in df.columns else 0.0
    adr = (ingresos / noches) if noches and noches > 0 else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reservas", f"{reservas:,}".replace(",", "."))
    c2.metric("Ingresos", f"{ingresos:,.0f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Noches", f"{int(noches):,}".replace(",", "."))
    c4.metric("ADR", (f"{adr:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")) if adr else "—")


def _top(df: pd.DataFrame, group_col: str, value_col: str, n=15) -> pd.DataFrame:
    d = df.copy()
    d = d.dropna(subset=[group_col])
    if d.empty:
        return pd.DataFrame({group_col: [], value_col: []})
    if value_col == "Reservas":
        t = d.groupby(group_col)["Localizador"].nunique().sort_values(ascending=False).head(n).reset_index()
        t.columns = [group_col, "Reservas"]
        return t
    else:
        t = d.groupby(group_col)[value_col].sum().sort_values(ascending=False).head(n).reset_index()
        t.columns = [group_col, value_col]
        return t


def render_mercados(df: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    # KPIs
    _kpi_row(df)
    st.divider()

    # TOPs (Reservas e Ingresos)
    st.markdown("### Top por Reservas")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.caption("Top País (Reservas)")
        tp = _top(df, "Pais", "Reservas", 15)
        st.plotly_chart(px.bar(tp, x="Reservas", y="Pais", orientation="h"), use_container_width=True)

    with c2:
        st.caption("Top Provincia (Reservas)")
        tv = _top(df, "Provincia", "Reservas", 15)
        st.plotly_chart(px.bar(tv, x="Reservas", y="Provincia", orientation="h"), use_container_width=True)

    with c3:
        st.caption("Top Idioma (Reservas)")
        ti = _top(df, "Idioma", "Reservas", 15)
        st.plotly_chart(px.bar(ti, x="Reservas", y="Idioma", orientation="h"), use_container_width=True)

    st.markdown("### Top por Ingresos")
    c4, c5, c6 = st.columns(3)

    with c4:
        st.caption("Top País (Ingresos)")
        tp2 = _top(df, "Pais", "Ingresos", 15)
        st.plotly_chart(px.bar(tp2, x="Ingresos", y="Pais", orientation="h"), use_container_width=True)

    with c5:
        st.caption("Top Provincia (Ingresos)")
        tv2 = _top(df, "Provincia", "Ingresos", 15)
        st.plotly_chart(px.bar(tv2, x="Ingresos", y="Provincia", orientation="h"), use_container_width=True)

    with c6:
        st.caption("Top Portal (Ingresos)")
        tpo = _top(df, "Portal", "Ingresos", 15)
        st.plotly_chart(px.bar(tpo, x="Ingresos", y="Portal", orientation="h"), use_container_width=True)

    st.divider()

    # Tendencia mensual (reservas / ingresos) con selector
    st.markdown("### Tendencia mensual (para decisiones de presupuesto)")
    col_sel, col_metric = st.columns([2, 1])

    with col_sel:
        dim = st.selectbox("Dimensión", ["Provincia", "Pais", "Portal"])
    with col_metric:
        met = st.selectbox("Métrica", ["Reservas", "Ingresos"])

    opts = sorted([x for x in df[dim].dropna().unique().tolist() if str(x).strip() != ""])
    selected = st.selectbox(f"Selecciona {dim}", opts) if opts else None

    if selected:
        dsel = df[df[dim] == selected].copy()
        if met == "Reservas":
            series = dsel.groupby("Mes")["Localizador"].nunique().reset_index(name="Reservas")
            st.plotly_chart(px.line(series, x="Mes", y="Reservas", markers=True), use_container_width=True)
        else:
            series = dsel.groupby("Mes")["Ingresos"].sum().reset_index(name="Ingresos")
            st.plotly_chart(px.line(series, x="Mes", y="Ingresos", markers=True), use_container_width=True)

    st.divider()

    # Heatmap Mes x Provincia (reservas) – súper Ads
    st.markdown("### Estacionalidad Ads: Mes x Provincia (Reservas)")
    dh = df.dropna(subset=["Mes", "Provincia"]).copy()
    if not dh.empty:
        heat = dh.pivot_table(index="Provincia", columns="Mes", values="Localizador", aggfunc=pd.Series.nunique, fill_value=0)
        heat = heat.sort_values(by=list(heat.columns)[-1], ascending=False).head(25)  # top 25 provincias
        st.plotly_chart(px.imshow(heat, aspect="auto"), use_container_width=True)
    else:
        st.info("No hay datos suficientes para el heatmap (faltan Mes/Provincia).")

    st.divider()

    # Lead time (ventana de reserva)
    st.markdown("### Lead time (ventana de reserva): cuándo impactar")
    dl = df.dropna(subset=["Lead_time_dias"]).copy()
    if not dl.empty:
        st.caption("Distribución global (días entre reserva y entrada)")
        st.plotly_chart(px.histogram(dl, x="Lead_time_dias", nbins=60), use_container_width=True)

        st.caption("Lead time medio por Provincia (Top 20 por volumen)")
        dprov = dl.dropna(subset=["Provincia"]).copy()
        if not dprov.empty:
            vol = dprov.groupby("Provincia")["Localizador"].nunique()
            top = vol.sort_values(ascending=False).head(20).index
            agg = dprov[dprov["Provincia"].isin(top)].groupby("Provincia")["Lead_time_dias"].mean().sort_values(ascending=False).reset_index()
            st.plotly_chart(px.bar(agg, x="Lead_time_dias", y="Provincia", orientation="h"), use_container_width=True)
    else:
        st.info("No hay lead time disponible (faltan fechas de alta/entrada en los archivos).")

    st.divider()

    # Provincia x Portal (reservas e ingresos)
    st.markdown("### Matriz Provincia x Portal (para estrategia de captura)")
    dp = df.dropna(subset=["Provincia", "Portal"]).copy()
    if not dp.empty:
        tab = dp.groupby(["Provincia", "Portal"]).agg(
            Reservas=("Localizador", "nunique"),
            Ingresos=("Ingresos", "sum"),
        ).reset_index()

        # top provincias por reservas para no sacar una tabla infinita
        top_prov = tab.groupby("Provincia")["Reservas"].sum().sort_values(ascending=False).head(30).index
        tab = tab[tab["Provincia"].isin(top_prov)].sort_values(["Reservas", "Ingresos"], ascending=False)

        st.dataframe(tab, use_container_width=True, height=420)
    else:
        st.info("No hay datos suficientes para Provincia x Portal.")

    st.divider()

    # Muestra de datos
    st.caption("Muestra de datos (post-filtro)")
    st.dataframe(df.head(300), use_container_width=True)
