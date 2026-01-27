import streamlit as st
import pandas as pd
import plotly.express as px

from core.formatting import eur, nint, pct


# ==========
# AJUSTA AQUÍ (si tus columnas se llaman diferente)
# ==========
COL_PAIS = "País"
COL_PROVINCIA = "Provincia"
COL_IDIOMA = "Idioma"

# Pon aquí el nombre EXACTO de tu columna dinero (la que suma ingresos).
# Ejemplos típicos: "Total ingresos", "Importe", "Revenue", "Total reserva"
COL_INGRESOS = "Total ingresos"

# Si tienes noches, pon su nombre exacto. Si no existe, deja None.
COL_NOCHES = "Noches"


def _safe_col(df: pd.DataFrame, col: str | None) -> bool:
    return (col is not None) and (col in df.columns)


def _top_counts(df: pd.DataFrame, col: str, n=15) -> pd.DataFrame:
    s = df[col].replace("", pd.NA).dropna()
    if s.empty:
        return pd.DataFrame({col: [], "Reservas": []})
    t = s.value_counts().head(n).reset_index()
    t.columns = [col, "Reservas"]
    return t


def _top_sum(df: pd.DataFrame, group_col: str, value_col: str, n=15) -> pd.DataFrame:
    d = df[[group_col, value_col]].copy()
    d = d.dropna(subset=[group_col, value_col])
    if d.empty:
        return pd.DataFrame({group_col: [], "Ingresos": []})
    t = d.groupby(group_col, as_index=False)[value_col].sum()
    t = t.sort_values("Ingresos", ascending=False).head(n)
    return t


def render_mercados(d: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    # ==========
    # KPIs BASE
    # ==========
    reservas = len(d)

    ingresos_total = None
    if _safe_col(d, COL_INGRESOS):
        ingresos_total = float(pd.to_numeric(d[COL_INGRESOS], errors="coerce").fillna(0).sum())

    adr = None
    if _safe_col(d, COL_INGRESOS) and _safe_col(d, COL_NOCHES):
        ingresos_num = pd.to_numeric(d[COL_INGRESOS], errors="coerce").fillna(0).sum()
        noches_num = pd.to_numeric(d[COL_NOCHES], errors="coerce").fillna(0).sum()
        adr = (ingresos_num / noches_num) if noches_num else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reservas", nint(reservas))
    c2.metric("Ingresos", eur(ingresos_total) if ingresos_total is not None else "—")
    c3.metric("ADR", eur(adr) if adr is not None else "—")
    c4.metric("Países activos", nint(d[COL_PAIS].nunique()) if _safe_col(d, COL_PAIS) else "—")

    st.divider()

    # ==========
    # BLOQUE 1: VOLUMEN (lo que ya tenías)
    # ==========
    st.markdown("### Volumen (quién nos visita)")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.caption("Top País (reservas)")
        if _safe_col(d, COL_PAIS):
            tp = _top_counts(d, COL_PAIS, 15)
            st.plotly_chart(px.bar(tp, x="Reservas", y=COL_PAIS, orientation="h"), use_container_width=True)
        else:
            st.info("No existe columna País.")

    with c2:
        st.caption("Top Provincia (reservas)")
        if _safe_col(d, COL_PROVINCIA):
            tv = _top_counts(d, COL_PROVINCIA, 15)
            st.plotly_chart(px.bar(tv, x="Reservas", y=COL_PROVINCIA, orientation="h"), use_container_width=True)
        else:
            st.info("No existe columna Provincia.")

    with c3:
        st.caption("Top Idioma (reservas)")
        if _safe_col(d, COL_IDIOMA):
            ti = _top_counts(d, COL_IDIOMA, 15)
            st.plotly_chart(px.bar(ti, x="Reservas", y=COL_IDIOMA, orientation="h"), use_container_width=True)
        else:
            st.info("No existe columna Idioma.")

    st.divider()

    # ==========
    # BLOQUE 2: VALOR (dinero)
    # ==========
    st.markdown("### Valor (quién nos deja más dinero)")

    if not _safe_col(d, COL_INGRESOS):
        st.warning(f"No encuentro la columna de ingresos '{COL_INGRESOS}'. Cámbiala arriba en COL_INGRESOS.")
        st.stop()

    # Top País por ingresos
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Top País (ingresos)")
        if _safe_col(d, COL_PAIS):
            tpi = _top_sum(d, COL_PAIS, COL_INGRESOS, 15)
            st.plotly_chart(px.bar(tpi, x="Ingresos", y=COL_PAIS, orientation="h"), use_container_width=True)
        else:
            st.info("No existe columna País.")

    # Dependencia top 1 / top 3 (muy útil marketing)
    with c2:
        st.caption("Dependencia de mercados (ingresos)")
        if _safe_col(d, COL_PAIS):
            tot = pd.to_numeric(d[COL_INGRESOS], errors="coerce").fillna(0).sum()
            share = (
                d.groupby(COL_PAIS)[COL_INGRESOS]
                .sum()
                .sort_values(ascending=False)
            )
            top1 = (share.iloc[0] / tot) if tot and len(share) >= 1 else None
            top3 = (share.iloc[:3].sum() / tot) if tot and len(share) >= 3 else None
            st.metric("% ingresos Top 1 país", pct(top1) if top1 is not None else "—")
            st.metric("% ingresos Top 3 países", pct(top3) if top3 is not None else "—")
        else:
            st.info("No existe columna País.")

    # ADR por país (si hay noches)
    if _safe_col(d, COL_PAIS) and _safe_col(d, COL_NOCHES):
        st.caption("ADR por país (filtrable por mínimo de reservas)")
        min_res = st.slider("Mínimo de reservas", 1, 50, 5)

        tmp = d[[COL_PAIS, COL_INGRESOS, COL_NOCHES]].copy()
        tmp[COL_INGRESOS] = pd.to_numeric(tmp[COL_INGRESOS], errors="coerce")
        tmp[COL_NOCHES] = pd.to_numeric(tmp[COL_NOCHES], errors="coerce")

        g = tmp.groupby(COL_PAIS, as_index=False).agg(
            Ingresos=(COL_INGRESOS, "sum"),
            Noches=(COL_NOCHES, "sum"),
            Reservas=(COL_PAIS, "size"),
        )
        g = g[g["Reservas"] >= min_res].copy()
        g["ADR"] = g["Ingresos"] / g["Noches"].replace(0, pd.NA)
        g = g.dropna(subset=["ADR"]).sort_values("ADR", ascending=False).head(20)

        st.plotly_chart(px.bar(g, x="ADR", y=COL_PAIS, orientation="h"), use_container_width=True)

    st.divider()

    # ==========
    # TABLA MARKETING (exportable)
    # ==========
    st.caption("Muestra de datos (post-filtro)")
    st.dataframe(d.head(200), use_container_width=True)
