import streamlit as st
import pandas as pd
import plotly.express as px
import re
import unicodedata


def _norm(s: str) -> str:
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s


def _find_col(df: pd.DataFrame, candidates_regex: list[str]) -> str | None:
    cols = list(df.columns)
    norm_map = {c: _norm(c) for c in cols}
    for c in cols:
        nc = norm_map[c]
        for pat in candidates_regex:
            if re.search(pat, nc):
                return c
    return None


def _top(df: pd.DataFrame, col: str, n: int = 15) -> pd.DataFrame:
    s = df[col].replace("", pd.NA).dropna()
    if s.empty:
        return pd.DataFrame({col: [], "Reservas": []})
    t = s.value_counts().head(n).reset_index()
    t.columns = [col, "Reservas"]
    return t


def render_mercados(df: pd.DataFrame):
    st.subheader("Mercados (Marketing)")

    # --- KPIs (si existen) ---
    # Reservas = filas
    reservas = len(df)

    ingresos = None
    noches = None
    adr = None

    if "Ingresos" in df.columns:
        ingresos = pd.to_numeric(df["Ingresos"], errors="coerce").fillna(0).sum()
    if "Noches" in df.columns:
        noches = pd.to_numeric(df["Noches"], errors="coerce").fillna(0).sum()
    if ingresos is not None and noches and noches > 0:
        adr = ingresos / noches

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reservas", f"{reservas:,}".replace(",", "."))
    c2.metric("Ingresos", "—" if ingresos is None else f"{ingresos:,.0f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Noches", "—" if noches is None else f"{int(noches):,}".replace(",", "."))
    c4.metric("ADR", "—" if adr is None else f"{adr:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

    st.divider()

    # --- Detectar columnas de mercado (muy robusto) ---
    col_pais = _find_col(df, [r"\bpais\b", r"\bcountry\b", r"ocupante:.*pais"])
    col_prov = _find_col(df, [r"\bprovincia\b", r"state|region", r"ocupante:.*prov"])
    col_idioma = _find_col(df, [r"\bidioma\b", r"\blanguage\b", r"ocupante:.*idioma"])

    if not col_pais and not col_prov and not col_idioma:
        st.info(
            "No encuentro columnas de **País / Provincia / Idioma** en el dataframe que llega a este dashboard.\n\n"
            "Esto suele pasar si estás visualizando solo el **LISTADO_RESERVAS** (que trae fechas/ingresos/noches) "
            "pero no el archivo **LISTA_RESERVAS** (que suele traer País/Provincia/Idioma/Portal)."
        )
        st.caption("Columnas detectadas en este archivo (primeras 25):")
        st.write(list(df.columns)[:25])
        return

    a, b, c = st.columns(3)

    if col_pais:
        with a:
            st.caption("Top País (Reservas)")
            tp = _top(df, col_pais, 15)
            st.plotly_chart(px.bar(tp, x="Reservas", y=col_pais, orientation="h"), use_container_width=True)
    else:
        with a:
            st.caption("Top País (Reservas)")
            st.warning("No hay columna de País en este archivo.")

    if col_prov:
        with b:
            st.caption("Top Provincia (Reservas)")
            tv = _top(df, col_prov, 15)
            st.plotly_chart(px.bar(tv, x="Reservas", y=col_prov, orientation="h"), use_container_width=True)
    else:
        with b:
            st.caption("Top Provincia (Reservas)")
            st.warning("No hay columna de Provincia en este archivo.")

    if col_idioma:
        with c:
            st.caption("Top Idioma (Reservas)")
            ti = _top(df, col_idioma, 15)
            st.plotly_chart(px.bar(ti, x="Reservas", y=col_idioma, orientation="h"), use_container_width=True)
    else:
        with c:
            st.caption("Top Idioma (Reservas)")
            st.warning("No hay columna de Idioma en este archivo.")

    st.divider()
    st.caption("Muestra de datos (post-filtro)")
    st.dataframe(df.head(200))
