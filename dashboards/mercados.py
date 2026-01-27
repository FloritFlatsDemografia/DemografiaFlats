import streamlit as st
import pandas as pd
import plotly.express as px


COL_PAIS = "País"
COL_PROV = "Provincia"
COL_IDIOMA = "Idioma"

COL_INGRESOS = "Total ingresos"
COL_NOCHES = "Noches"


def _safe_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col in df.columns:
        return df[col]
    return pd.Series([pd.NA] * len(df))


def _top_count(df: pd.DataFrame, col: str, n: int = 15) -> pd.DataFrame:
    s = _safe_series(df, col).replace("", pd.NA).dropna()
    if s.empty:
        return pd.DataFrame({col: [], "Reservas": []})
    t = s.value_counts().head(n).reset_index()
    t.columns = [col, "Reservas"]
    return t


def _top_sum(df: pd.DataFrame, group_col: str, value_col: str, n: int = 15, out_name: str = "Ingresos") -> pd.DataFrame:
    if group_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame({group_col: [], out_name: []})

    d = df[[group_col, value_col]].copy()
    d = d.dropna(subset=[group_col])
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[value_col])

    if d.empty:
        return pd.DataFrame({group_col: [], out_name: []})

    t = d.groupby(group_col, dropna=True)[value_col].sum().sort_values(ascending=False).head(n).reset_index()
    t.columns = [group_col, out_name]
    return t


def _top_adr(df: pd.DataFrame, group_col: str, ingresos_col: str, noches_col: str, n: int = 15) -> pd.DataFrame:
    if group_col not in df.columns or ingresos_col not in df.columns or noches_col not in df.columns:
        return pd.DataFrame({group_col: [], "ADR": []})

    d = df[[group_col, ingresos_col, noches_col]].copy()
    d = d.dropna(subset=[group_col])
    d[ingresos_col] = pd.to_numeric(d[ingresos_col], errors="coerce")
    d[noches_col] = pd.to_numeric(d[noches_col], errors="coerce")
    d = d.dropna(subset=[ingresos_col, noches_col])
    d = d[d[noches_col] > 0]

    if d.empty:
        return pd.DataFrame({group_col: [], "ADR": []})

    agg = d.groupby(group_col, dropna=True).agg(
        Ingresos=(ingresos_col, "sum"),
        Noches=(noches_col, "sum"),
        Reservas=(group_col, "size"),
    ).reset_index()

    agg["ADR"] = agg["Ingresos"] / agg["Noches"]
    agg = agg.sort_values("ADR", ascending=False).head(n)

    return agg[[group_col, "ADR", "Ingresos", "Noches", "Reservas"]]


def render_mercados(d: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    # KPIs (si existen columnas de dinero/noches)
    ingresos_total = pd.to_numeric(_safe_series(d, COL_INGRESOS), errors="coerce").sum(skipna=True) if COL_INGRESOS in d.columns else None
    noches_total = pd.to_numeric(_safe_series(d, COL_NOCHES), errors="coerce").sum(skipna=True) if COL_NOCHES in d.columns else None
    reservas_total = len(d)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Reservas", f"{reservas_total:,}".replace(",", "."))
    with k2:
        if ingresos_total is None or pd.isna(ingresos_total):
            st.metric("Ingresos", "—")
        else:
            st.metric("Ingresos", f"{ingresos_total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    with k3:
        if noches_total is None or pd.isna(noches_total):
            st.metric("Noches", "—")
        else:
            st.metric("Noches", f"{int(noches_total):,}".replace(",", "."))
    with k4:
        if ingresos_total is None or noches_total is None or noches_total == 0 or pd.isna(noches_total):
            st.metric("ADR", "—")
        else:
            adr = ingresos_total / noches_total
            st.metric("ADR", f"{adr:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

    st.divider()

    # 3 gráficos "reservas" (los que ya tenías)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.caption("Top País (Reservas)")
        tp = _top_count(d, COL_PAIS, 15)
        st.plotly_chart(px.bar(tp, x="Reservas", y=COL_PAIS, orientation="h"), use_container_width=True)

    with c2:
        st.caption("Top Provincia (Reservas)")
        tv = _top_count(d, COL_PROV, 15)
        st.plotly_chart(px.bar(tv, x="Reservas", y=COL_PROV, orientation="h"), use_container_width=True)

    with c3:
        st.caption("Top Idioma (Reservas)")
        ti = _top_count(d, COL_IDIOMA, 15)
        st.plotly_chart(px.bar(ti, x="Reservas", y=COL_IDIOMA, orientation="h"), use_container_width=True)

    st.divider()

    # 2 gráficos de dinero (si existen columnas)
    if (COL_INGRESOS in d.columns) and (pd.to_numeric(d[COL_INGRESOS], errors="coerce").notna().any()):
        c4, c5 = st.columns(2)

        with c4:
            st.caption("Top País (Ingresos)")
            t_ing = _top_sum(d, COL_PAIS, COL_INGRESOS, 15, out_name="Ingresos")
            st.plotly_chart(px.bar(t_ing, x="Ingresos", y=COL_PAIS, orientation="h"), use_container_width=True)

        with c5:
            st.caption("ADR por País (Ingresos / Noches)")
            if (COL_NOCHES in d.columns) and (pd.to_numeric(d[COL_NOCHES], errors="coerce").notna().any()):
                t_adr = _top_adr(d, COL_PAIS, COL_INGRESOS, COL_NOCHES, 15)
                # Mostramos ADR (con hover de ingresos/noches)
                if not t_adr.empty:
                    fig = px.bar(t_adr, x="ADR", y=COL_PAIS, orientation="h", hover_data=["Ingresos", "Noches", "Reservas"])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay datos suficientes para ADR (revisa fechas de entrada/salida).")
            else:
                st.info("Falta la columna 'Noches'. Asegúrate de que cleaning.py esté actualizado.")
    else:
        st.info("No se detectaron ingresos. Revisa que la columna M del Excel sea 'Total reserva…' (o similar).")

    st.divider()
    st.caption("Muestra de datos (post-filtro)")
    st.dataframe(d.head(200))
