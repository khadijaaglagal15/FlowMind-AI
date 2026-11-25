import re
from datetime import timedelta

import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

API_URL = "http://127.0.0.1:8000"

# ------------------------------------------------------------------ Palette
BG = "#F7F9F8"
CARD = "#FFFFFF"
BORDER = "#E3EBE8"
INK = "#172B2A"
MUTED = "#64748B"
PRIMARY = "#0F766E"
PRIMARY_DARK = "#0B5E58"
PRIMARY_TINT = "#E7F4F1"
SECONDARY = "#14B8A6"
SLATE = "#94A3B8"
UP = "#15803D"
DOWN = "#B42318"

# One discreet accent per KPI card (teal family + neutrals)
KPI_ACCENTS = [PRIMARY, SECONDARY, "#334E68", "#B8935A", "#6B8E83"]

SEQUENCE = [PRIMARY, SECONDARY, "#7FCFC2", "#A7B8B4", "#334E68", "#CBD5D1", "#B8935A", "#6B8E83"]
SCALE_TEAL = ["#E7F4F1", SECONDARY, PRIMARY]
SCALE_HEAT = ["#F3F9F8", SECONDARY, PRIMARY]

st.set_page_config(
    page_title="FlowMind AI - Sales Intelligence & Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit >= 1.50 replaces use_container_width with width="stretch"
_ver = [int(x) for x in re.findall(r"\d+", st.__version__)[:2]]
FW = {"width": "stretch"} if _ver >= [1, 50] else {"use_container_width": True}

# ---------------------------------------------------------------- Style (CSS)
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: __BG__; color: __INK__; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }
h1, h2, h3, h4 { color: __INK__; letter-spacing: -.01em; }
html { scroll-behavior: smooth; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: __CARD__; border-right: 1px solid __BORDER__; }
[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
.brand { display:flex; align-items:center; gap:12px; margin-bottom:14px; }
.brand-name { font-weight:700; font-size:1.05rem; color:__INK__; line-height:1.2; }
.brand-tag { font-size:.74rem; color:__MUTED__; }
.side-title { font-size:.78rem; font-weight:600; color:__MUTED__; margin:2px 0 6px 0; }
.status { display:inline-flex; align-items:center; gap:8px; padding:6px 12px; border-radius:999px;
          font-size:.8rem; font-weight:500; border:1px solid __BORDER__; }
.status i { width:8px; height:8px; border-radius:50%; display:inline-block; }
.status.ok { background:#EEF8F5; color:__PRIMARY__; border-color:#CFE7E1; }
.status.ok i { background:#16A37F; }
.status.ko { background:#FDF1F0; color:#B42318; border-color:#F5D0CC; }
.status.ko i { background:#D92D20; }
a.nav-link {
    display:block; padding:8px 12px; border-radius:8px; margin-bottom:2px;
    color:__INK__ !important; text-decoration:none !important; font-size:.92rem; font-weight:500;
    transition:background .15s ease, color .15s ease;
}
a.nav-link:hover { background:__PRIMARY_TINT__; color:__PRIMARY__ !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] { background:__PRIMARY_TINT__ !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] span { color:__PRIMARY__ !important; }

/* ---------- Page header ---------- */
.page-header { margin-bottom:1.1rem; }
.page-title { font-size:1.85rem; font-weight:700; margin:0; color:__INK__; letter-spacing:-.02em; }
.page-sub { font-size:1rem; font-weight:600; color:__PRIMARY__; margin:2px 0 0 0; }
.page-desc { font-size:.9rem; color:__MUTED__; margin:6px 0 0 0; max-width:780px; line-height:1.5; }

/* ---------- Cards (keyed containers created by card()) ---------- */
[class*="st-key-card_"] {
    background:__CARD__; border:1px solid __BORDER__; border-radius:14px;
    padding:1.1rem 1.3rem; box-shadow:0 1px 2px rgba(23,43,42,.04), 0 4px 14px rgba(23,43,42,.04);
    transition:box-shadow .2s ease, border-color .2s ease;
}
[class*="st-key-card_"]:hover { border-color:#CFE0DB; box-shadow:0 2px 4px rgba(23,43,42,.05), 0 8px 22px rgba(23,43,42,.06); }
[class*="st-key-card_"] [class*="st-key-card_"] { box-shadow:none; background:#FAFCFB; border-radius:12px; }
.card-title { font-size:.98rem; font-weight:600; color:__INK__; margin:0; }
.card-sub { font-size:.82rem; color:__MUTED__; margin:2px 0 0 0; }

/* ---------- KPI cards ---------- */
.kpi {
    background:__CARD__; border:1px solid __BORDER__; border-top:3px solid var(--accent);
    border-radius:14px; padding:14px 18px; min-height:132px;
    display:flex; flex-direction:column; justify-content:space-between;
    box-shadow:0 1px 2px rgba(23,43,42,.04), 0 4px 14px rgba(23,43,42,.04);
    transition:transform .18s ease, box-shadow .18s ease;
}
.kpi:hover { transform:translateY(-2px); box-shadow:0 2px 4px rgba(23,43,42,.05), 0 10px 24px rgba(23,43,42,.07); }
.kpi-label { font-size:.82rem; color:__MUTED__; font-weight:500; }
.kpi-row { display:flex; align-items:flex-end; justify-content:space-between; gap:8px; }
.kpi-value { font-size:1.7rem; font-weight:700; letter-spacing:-.02em; color:__INK__; line-height:1.15;
             font-variant-numeric:tabular-nums; }
.kpi-delta { font-size:.76rem; font-weight:600; margin-top:3px; }
.kpi-delta span { color:__MUTED__; font-weight:400; margin-left:4px; }
.kpi-delta.up { color:__UP__; }
.kpi-delta.down { color:__DOWN__; }
.kpi-delta.flat { color:__MUTED__; }

/* ---------- st.metric ---------- */
[data-testid="stMetric"] { background:__CARD__; border:1px solid __BORDER__; border-radius:12px; padding:12px 16px; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color:__MUTED__ !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    color:__PRIMARY__ !important; font-weight:700; letter-spacing:-.02em; font-variant-numeric:tabular-nums;
}
[data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * { font-weight:600; }

/* Textes lisibles dans les cartes, quel que soit le thème Streamlit (clair / sombre) */
:root { color-scheme: light; }
[class*="st-key-card_"] [data-testid="stMarkdownContainer"] p,
[class*="st-key-card_"] [data-testid="stMarkdownContainer"] strong,
[class*="st-key-card_"] [data-testid="stMarkdownContainer"] li { color:__INK__; }
[class*="st-key-card_"] .card-sub { color:__MUTED__; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color:__MUTED__ !important; }
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * { color:__INK__ !important; }
[data-testid="stRadio"] label p, [data-testid="stToggle"] label p { color:__INK__ !important; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap:2px; border-bottom:1px solid __BORDER__; }
.stTabs [data-baseweb="tab"] { background:transparent; padding:10px 16px; font-weight:500; color:__MUTED__; }
.stTabs [aria-selected="true"] { color:__PRIMARY__ !important; font-weight:600; }
.stTabs [data-baseweb="tab-highlight"] { background-color:__PRIMARY__; }

/* ---------- Buttons / inputs ---------- */
.stButton > button, .stDownloadButton > button {
    border-radius:10px; border:1px solid __BORDER__; background:__CARD__; color:__INK__; font-weight:500;
    transition:border-color .15s ease, color .15s ease, background .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover { border-color:__PRIMARY__; color:__PRIMARY__; }
button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background:__PRIMARY__ !important; border-color:__PRIMARY__ !important; color:#fff !important;
}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
    background:__PRIMARY_DARK__ !important; border-color:__PRIMARY_DARK__ !important; color:#fff !important;
}
[data-testid="stSlider"] [role="slider"] { background-color:__PRIMARY__ !important; border-color:__PRIMARY__ !important; }
[data-testid="stSliderThumbValue"] { color:__PRIMARY__ !important; }

/* ---------- Insight ---------- */
.insight {
    background:__PRIMARY_TINT__; border-left:3px solid __PRIMARY__; border-radius:10px;
    padding:12px 16px; margin:10px 0 4px 0; color:__INK__; font-size:.92rem;
}

/* ---------- Forecast section ---------- */
.fc-banner {
    background:__PRIMARY__; color:#fff; border-radius:16px; padding:22px 28px; margin:0 0 1rem 0;
    box-shadow:0 4px 18px rgba(15,118,110,.22);
}
.fc-banner h2 { color:#fff; margin:0; font-size:1.4rem; font-weight:700; }
.fc-banner p { margin:6px 0 0 0; opacity:.9; font-size:.92rem; max-width:780px; line-height:1.5; }
.timeline { display:flex; gap:6px; margin:4px 0 8px 0; }
.tl-block { border-radius:10px; padding:10px 14px; font-size:.82rem; }
.tl-block b { display:block; font-size:.86rem; margin-bottom:2px; }
.tl-hist { flex:4; background:#EEF2F1; color:__INK__; border:1px solid __BORDER__; }
.tl-fc { flex:1.4; background:__PRIMARY_TINT__; color:__PRIMARY__; border:1px dashed __PRIMARY__; }
.mae { background:__CARD__; border:1px solid __BORDER__; border-radius:14px; padding:16px 18px; min-height:110px;
       box-shadow:0 1px 2px rgba(23,43,42,.04), 0 4px 14px rgba(23,43,42,.04); }
.mae.best { border-color:__PRIMARY__; background:#F5FAF9; }
.mae-label { font-size:.82rem; color:__MUTED__; font-weight:500; display:flex; justify-content:space-between; gap:8px; }
.mae-tag { font-size:.68rem; font-weight:600; color:__PRIMARY__; background:__PRIMARY_TINT__;
           padding:2px 8px; border-radius:999px; white-space:nowrap; }
.mae-value { font-size:1.6rem; font-weight:700; color:__INK__; margin-top:8px; font-variant-numeric:tabular-nums; }

@media (max-width: 900px) {
    .page-title { font-size:1.5rem; }
    .kpi { min-height:0; margin-bottom:8px; }
    .timeline { flex-direction:column; }
}
</style>
"""
TOKENS = {
    "__BG__": BG, "__CARD__": CARD, "__BORDER__": BORDER, "__INK__": INK, "__MUTED__": MUTED,
    "__PRIMARY__": PRIMARY, "__PRIMARY_DARK__": PRIMARY_DARK, "__PRIMARY_TINT__": PRIMARY_TINT,
}
for token, value in TOKENS.items():
    CSS = CSS.replace(token, value)
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ Données
@st.cache_data(ttl=10)
def check_backend() -> bool:
    try:
        requests.get(f"{API_URL}/health", timeout=3).raise_for_status()
        return True
    except requests.RequestException:
        return False


@st.cache_data(ttl=300, show_spinner="Chargement des statistiques globales…")
def load_global_stats() -> dict:
    response = requests.get(f"{API_URL}/analytics/retail", timeout=60)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=300, show_spinner="Chargement des transactions…")
def load_transactions(limit: int) -> pd.DataFrame:
    response = requests.get(
        f"{API_URL}/retail/transactions", params={"limit": limit}, timeout=60
    )
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    if df.empty:
        return df
    if "invoice_date" in df:
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    if "total_amount" not in df and {"quantity", "unit_price"} <= set(df.columns):
        df["total_amount"] = df["quantity"] * df["unit_price"]
    return df


# ------------------------------------------------------------ Composants UI
_card_counter = 0


def card():
    """Carte à bordure : conteneur à clé (Streamlit >= 1.39) stylé en CSS,
    avec repli sur le conteneur natif pour les versions plus anciennes."""
    global _card_counter
    _card_counter += 1
    try:
        return st.container(key=f"card_{_card_counter}")
    except TypeError:
        return st.container(border=True)


def card_header(title: str, subtitle: str = "") -> None:
    html = f'<p class="card-title">{title}</p>'
    if subtitle:
        html += f'<p class="card-sub">{subtitle}</p>'
    st.markdown(html, unsafe_allow_html=True)


def style_fig(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=INK, size=12),
        margin=dict(l=8, r=16, t=48, b=8),
        title=dict(font=dict(size=15, color=INK), x=0, xanchor="left"),
        hoverlabel=dict(bgcolor="white", bordercolor=BORDER, font=dict(color=INK, size=12)),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center", title=None),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(color=MUTED), title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor="#EEF2F1", zeroline=False, tickfont=dict(color=MUTED), title_font=dict(color=MUTED))
    return fig


def sparkline(values, color=PRIMARY, w=110, h=40, pad=4) -> str:
    """Mini courbe SVG avec aire légère et point final."""
    values = [float(v) for v in values]
    n = len(values)
    if n < 2:
        return ""
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1.0
    pts = [
        (pad + i * (w - 2 * pad) / (n - 1), h - pad - (v - lo) / rng * (h - 2 * pad))
        for i, v in enumerate(values)
    ]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = (
        f"M{pts[0][0]:.1f},{h} L"
        + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        + f" L{pts[-1][0]:.1f},{h} Z"
    )
    ex, ey = pts[-1]
    return (
        f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">'
        f'<path d="{area}" fill="{color}" fill-opacity=".12"/>'
        f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="2.6" fill="{color}"/></svg>'
    )


def kpi_card(label, value, current, previous, series, accent=PRIMARY) -> str:
    if previous not in (None, 0) and current is not None:
        pct = (current - previous) / previous * 100
        cls = "up" if pct > 0 else "down" if pct < 0 else "flat"
        arrow = "▲" if pct > 0 else "▼" if pct < 0 else "•"
        delta = f'<div class="kpi-delta {cls}">{arrow} {abs(pct):.1f}%<span>vs période préc.</span></div>'
    else:
        delta = '<div class="kpi-delta flat">—<span>pas de période préc.</span></div>'
    return (
        f'<div class="kpi" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        '<div class="kpi-row">'
        f'<div><div class="kpi-value">{value}</div>{delta}</div>'
        f'<div>{sparkline(series)}</div>'
        "</div></div>"
    )


def kpi_values(d: pd.DataFrame) -> dict:
    if d.empty:
        return dict(n=0, revenue=0.0, avg=None, products=0, countries=0)
    return dict(
        n=len(d),
        revenue=float(d["total_amount"].sum()),
        avg=float(d["total_amount"].mean()),
        products=int(d["description"].nunique()),
        countries=int(d["country"].nunique()),
    )


def daily(d: pd.DataFrame, how) -> list:
    dated = d.dropna(subset=["invoice_date"])
    if dated.empty:
        return []
    g = dated.groupby(dated["invoice_date"].dt.date)
    return how(g).tolist()


def area_chart(data, x, y, title, height):
    """Courbe d'aire cohérente pour toutes les séries de CA (mêmes données qu'avant)."""
    fig = px.area(
        data, x=x, y=y, title=title,
        color_discrete_sequence=[PRIMARY],
        labels={x: "", y: "CA (£)"},
    )
    fig.update_traces(
        fillcolor="rgba(15,118,110,.10)", line=dict(width=2),
        mode="lines+markers", marker=dict(size=5),
        hovertemplate="CA : %{y:,.0f} £<extra></extra>",
    )
    fig.update_layout(hovermode="x unified")
    return style_fig(fig, height)


# ------------------------------------------------------------------ Sidebar
LOGO = (
    '<svg width="34" height="34" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">'
    f'<rect width="32" height="32" rx="9" fill="{PRIMARY}"/>'
    '<path d="M7 20c3-9 6-9 8-4s5 4 10-5" fill="none" stroke="#fff" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

with st.sidebar:
    st.markdown(
        f'<div class="brand">{LOGO}<div><div class="brand-name">FlowMind AI</div>'
        '<div class="brand-tag">Sales Intelligence &amp; Automation</div></div></div>',
        unsafe_allow_html=True,
    )
    backend_ok = check_backend()
    if backend_ok:
        st.markdown('<span class="status ok"><i></i>Backend connecté</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status ko"><i></i>Backend indisponible</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="side-title">Navigation</div>', unsafe_allow_html=True)
    st.markdown(
        '<a class="nav-link" href="#dashboard" target="_self">Tableau de bord</a>'
        '<a class="nav-link" href="#forecast" target="_self">Prévisions</a>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown('<div class="side-title">Données</div>', unsafe_allow_html=True)
    limit = st.select_slider(
        "Nombre de transactions à charger",
        options=[100, 500, 1000, 5000],
        value=1000,
    )
    if st.button("Actualiser les données", **FW):
        st.cache_data.clear()
        st.rerun()


def page_header() -> None:
    st.markdown(
        '<div id="dashboard"></div>'
        '<div class="page-header">'
        '<p class="page-title">FlowMind AI</p>'
        '<p class="page-sub">Sales Intelligence &amp; Analytics</p>'
        '<p class="page-desc">Analysez les transactions, repérez les meilleurs produits, '
        "comparez les performances par pays et anticipez le chiffre d'affaires grâce aux prévisions.</p>"
        "</div>",
        unsafe_allow_html=True,
    )


if not backend_ok:
    page_header()
    st.error("Backend non disponible. Lancez d'abord FastAPI : `uvicorn main:app --reload`")
    st.stop()

try:
    df_all = load_transactions(limit)
except requests.RequestException as error:
    st.error(f"Impossible de charger les transactions : {error}")
    st.stop()

if df_all.empty:
    st.info("Aucune transaction disponible.")
    st.stop()

# Filtres (dépendent des données chargées)
with st.sidebar:
    st.divider()
    st.markdown('<div class="side-title">Filtres</div>', unsafe_allow_html=True)

    countries = sorted(df_all["country"].dropna().unique())
    selected_countries = st.multiselect("Pays", countries, placeholder="Tous les pays")

    search = st.text_input("Produit", placeholder="ex : LANTERN")

    if df_all["invoice_date"].notna().any():
        min_date = df_all["invoice_date"].min().date()
        max_date = df_all["invoice_date"].max().date()
        date_range = st.date_input(
            "Période", value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )
    else:
        date_range = None

# ------------------------------------------------------------------ En-tête
page_header()

# Base = filtres pays/produit, sans la date (sert aussi à la période précédente)
base = df_all.copy()
if selected_countries:
    base = base[base["country"].isin(selected_countries)]
if search:
    base = base[base["description"].str.contains(search, case=False, na=False)]

df = base.copy()
prev_df = None
if date_range and len(date_range) == 2:
    start, end = date_range
    df = base[
        base["invoice_date"].dt.date.between(start, end) | base["invoice_date"].isna()
    ]
    span = (end - start).days + 1
    prev_start = start - timedelta(days=span)
    prev_end = start - timedelta(days=1)
    prev_df = base[base["invoice_date"].dt.date.between(prev_start, prev_end)]

if df.empty:
    st.warning("Aucune transaction ne correspond aux filtres choisis.")
    st.stop()

# KPI (calculés sur les données filtrées, comparés à la période précédente)
cur = kpi_values(df)
prev = kpi_values(prev_df) if prev_df is not None and not prev_df.empty else None

cards = [
    ("Transactions", f"{cur['n']:,}", cur["n"], prev and prev["n"],
     daily(df, lambda g: g.size())),
    ("Chiffre d'affaires", f"{cur['revenue']:,.0f} £", cur["revenue"], prev and prev["revenue"],
     daily(df, lambda g: g["total_amount"].sum())),
    ("Transaction moyenne", f"{cur['avg']:,.2f} £", cur["avg"], prev and prev["avg"],
     daily(df, lambda g: g["total_amount"].mean())),
    ("Produits distincts", f"{cur['products']:,}", cur["products"], prev and prev["products"],
     daily(df, lambda g: g["description"].nunique())),
    ("Pays", f"{cur['countries']:,}", cur["countries"], prev and prev["countries"],
     daily(df, lambda g: g["country"].nunique())),
]
for col, (label, value, c, p, series), accent in zip(st.columns(5), cards, KPI_ACCENTS):
    col.markdown(kpi_card(label, value, c, p, series, accent), unsafe_allow_html=True)

st.caption(
    f"Vue basée sur {len(df):,} transactions filtrées "
    f"(sur {len(df_all):,} chargées depuis l'API)."
)

# ------------------------------------------------------------------ Onglets
tab_home, tab_products, tab_countries, tab_time, tab_table = st.tabs(
    ["Vue d'ensemble", "Produits", "Pays", "Évolution", "Transactions"]
)

# ---- Vue d'ensemble
with tab_home:
    with card():
        card_header(
            "Indicateurs globaux du dataset",
            "Calculés par le backend sur l'ensemble des données, sans filtre.",
        )
        try:
            stats = load_global_stats()
            g1, g2, g3 = st.columns(3)
            g1.metric("Transactions (total)", f'{stats["total_transactions"]:,}')
            g2.metric("Chiffre d'affaires (total)", f'{stats["total_revenue"]:,.2f} £')
            g3.metric("Transaction moyenne (total)", f'{stats["average_transaction"]:,.2f} £')

            best = stats.get("best_selling_product")
            top = stats.get("top_country")
            c1, c2 = st.columns(2)
            with c1:
                with card():
                    card_header("Produit le plus vendu")
                    if best:
                        st.markdown(f"**{best['product']}**")
                        st.metric("Quantité vendue", f"{best['quantity_sold']:,}")
                    else:
                        st.info("Aucun produit disponible.")
            with c2:
                with card():
                    card_header("Pays avec le plus de revenus")
                    if top:
                        st.markdown(f"**{top['country']}**")
                        st.metric("Chiffre d'affaires", f"{top['revenue']:,.2f} £")
                    else:
                        st.info("Aucun pays disponible.")
        except requests.RequestException as error:
            st.error(f"Impossible de charger les statistiques : {error}")
        except (KeyError, ValueError) as error:
            st.error(f"Erreur dans les données reçues : {error}")

    left, right = st.columns([3, 2])
    with left:
        with card():
            by_day = (
                df.dropna(subset=["invoice_date"])
                .assign(date=lambda d: d["invoice_date"].dt.date)
                .groupby("date", as_index=False)["total_amount"].sum()
            )
            fig = area_chart(by_day, "date", "total_amount", "Chiffre d'affaires par jour", 340)
            st.plotly_chart(fig, **FW)
    with right:
        with card():
            dated_home = df.dropna(subset=["invoice_date"])
            if dated_home.empty:
                st.info("Aucune date exploitable dans les données.")
            else:
                top_countries = df.groupby("country")["total_amount"].sum().nlargest(4).index
                span_days = (dated_home["invoice_date"].max() - dated_home["invoice_date"].min()).days
                stack_freq = "D" if span_days <= 45 else "W"
                stacked = (
                    dated_home.assign(
                        groupe=lambda d: d["country"].where(d["country"].isin(top_countries), "Autres")
                    )
                    .groupby([pd.Grouper(key="invoice_date", freq=stack_freq), "groupe"])["total_amount"]
                    .sum().reset_index()
                )
                fig = px.bar(
                    stacked, x="invoice_date", y="total_amount", color="groupe",
                    title="CA par pays dans le temps", barmode="stack",
                    color_discrete_sequence=SEQUENCE,
                    labels={"invoice_date": "", "total_amount": "CA (£)", "groupe": "Pays"},
                )
                fig.update_traces(hovertemplate="%{fullData.name} : %{y:,.0f} £<extra></extra>")
                fig.update_layout(hovermode="x unified")
                st.plotly_chart(style_fig(fig, 340), **FW)

    # Tableau "Top produits"
    with card():
        t1, t2 = st.columns([4, 1])
        with t1:
            card_header("Top produits")
        top_table = (
            df.groupby("description")
            .agg(
                quantite=("quantity", "sum") if "quantity" in df else ("total_amount", "size"),
                revenu=("total_amount", "sum"),
                transactions=("total_amount", "size"),
                moyenne=("total_amount", "mean"),
                pays=("country", "nunique"),
            )
            .sort_values("revenu", ascending=False)
            .head(10)
            .reset_index()
        )
        with t2:
            st.download_button(
                "Exporter",
                data=top_table.to_csv(index=False).encode("utf-8"),
                file_name="top_produits.csv",
                mime="text/csv",
                **FW,
            )
        st.dataframe(
            top_table, hide_index=True,
            column_config={
                "description": "Produit",
                "quantite": st.column_config.NumberColumn("Quantité", format="%d"),
                "revenu": st.column_config.ProgressColumn(
                    "CA (£)", format="%.0f", min_value=0,
                    max_value=float(top_table["revenu"].max()),
                ),
                "transactions": "Transactions",
                "moyenne": st.column_config.NumberColumn("Moyenne (£)", format="%.2f"),
                "pays": "Pays",
            },
            **FW,
        )
        st.caption(f"Affichage des {len(top_table)} premiers produits sur {df['description'].nunique():,}")

# ---- Produits
with tab_products:
    with card():
        c1, c2 = st.columns([1, 1])
        metric_choice = c1.radio(
            "Classer les produits par", ["Quantité vendue", "Chiffre d'affaires"],
            horizontal=True,
        )
        top_n = c2.slider("Nombre de produits", 5, 30, 10)

        col = "quantity" if metric_choice == "Quantité vendue" else "total_amount"
        products = (
            df.groupby("description")[col].sum().nlargest(top_n).sort_values().reset_index()
        )
        fig = px.bar(
            products, x=col, y="description", orientation="h",
            color=col, color_continuous_scale=SCALE_TEAL,
            title=f"Top {top_n} des produits – {metric_choice.lower()}",
            labels={col: metric_choice, "description": ""},
        )
        unit = "unités" if col == "quantity" else "£"
        fig.update_traces(
            texttemplate="%{x:,.0f}", textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} " + unit + "<extra></extra>",
        )
        fig.update_coloraxes(showscale=False)
        fig.update_layout(margin=dict(l=8, r=56, t=48, b=8))
        st.plotly_chart(style_fig(fig, 90 + top_n * 32), **FW)

        leader = products.iloc[-1]
        st.markdown(
            f'<div class="insight"><b>{leader["description"]}</b> arrive en tête '
            f"avec {leader[col]:,.0f} {'unités' if col == 'quantity' else '£'}.</div>",
            unsafe_allow_html=True,
        )

# ---- Pays
with tab_countries:
    by_country = df.groupby("country", as_index=False).agg(
        revenue=("total_amount", "sum"),
        transactions=("total_amount", "size"),
        average=("total_amount", "mean"),
    )
    with card():
        view = st.radio("Affichage", ["Carte", "Barres", "Treemap", "Donut"], horizontal=True)

        if view == "Carte":
            fig = px.choropleth(
                by_country, locations="country", locationmode="country names",
                color="revenue", hover_data=["transactions", "average"],
                color_continuous_scale=SCALE_TEAL,
                title="Chiffre d'affaires par pays",
            )
            fig.update_traces(
                hovertemplate="<b>%{location}</b><br>CA : %{z:,.0f} £"
                "<br>Transactions : %{customdata[0]:,}"
                "<br>Moyenne : %{customdata[1]:,.2f} £<extra></extra>",
                marker_line_color="white", marker_line_width=.5,
            )
            fig.update_geos(
                showframe=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)",
                showcountries=True, countrycolor=BORDER, landcolor="#F1F5F4",
            )
            fig.update_coloraxes(colorbar=dict(title="CA (£)", thickness=10, len=.6))
            st.plotly_chart(style_fig(fig, 480), **FW)
        elif view == "Barres":
            top_c = by_country.nlargest(10, "revenue").sort_values("revenue")
            fig = px.bar(
                top_c, x="revenue", y="country", orientation="h",
                color="revenue", color_continuous_scale=SCALE_TEAL,
                title="Top 10 des pays par chiffre d'affaires",
                labels={"revenue": "CA (£)", "country": ""},
            )
            fig.update_traces(
                texttemplate="%{x:,.0f} £", textposition="outside", cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>%{x:,.0f} £<extra></extra>",
            )
            fig.update_coloraxes(showscale=False)
            fig.update_layout(margin=dict(l=8, r=72, t=48, b=8))
            st.plotly_chart(style_fig(fig, 460), **FW)
        elif view == "Treemap":
            fig = px.treemap(
                by_country, path=["country"], values="revenue",
                color="average", color_continuous_scale=SCALE_TEAL,
                title="Poids de chaque pays (couleur = transaction moyenne)",
            )
            fig.update_traces(
                hovertemplate="<b>%{label}</b><br>CA : %{value:,.0f} £"
                "<br>Moyenne : %{color:,.2f} £<extra></extra>",
                marker_line_color="white",
            )
            fig.update_coloraxes(colorbar=dict(title="Moy. (£)", thickness=10, len=.6))
            st.plotly_chart(style_fig(fig, 480), **FW)
        else:
            share = df.groupby("country")["total_amount"].sum().nlargest(6).reset_index()
            fig = px.pie(
                share, names="country", values="total_amount", hole=0.6,
                title="Répartition du CA (top 6 pays)",
                color_discrete_sequence=SEQUENCE,
            )
            fig.update_traces(
                textinfo="percent", pull=[0.04] + [0] * (len(share) - 1),
                marker=dict(line=dict(color="white", width=2)),
                hovertemplate="<b>%{label}</b><br>%{value:,.0f} £ (%{percent})<extra></extra>",
            )
            st.plotly_chart(style_fig(fig, 480), **FW)

    with card():
        card_header("Détail par pays")
        st.dataframe(
            by_country.sort_values("revenue", ascending=False),
            hide_index=True,
            column_config={
                "country": "Pays",
                "revenue": st.column_config.NumberColumn("CA (£)", format="%.0f"),
                "transactions": "Transactions",
                "average": st.column_config.NumberColumn("Moyenne (£)", format="%.2f"),
            },
            **FW,
        )

# ---- Évolution
with tab_time:
    dated = df.dropna(subset=["invoice_date"])
    if dated.empty:
        st.info("Aucune date exploitable dans les données.")
    else:
        with card():
            c1, c2 = st.columns([2, 1])
            freq_label = c1.radio("Regrouper par", ["Jour", "Semaine", "Mois"], horizontal=True)
            cumulative = c2.toggle("Cumul")
            freq = {"Jour": "D", "Semaine": "W", "Mois": "MS"}[freq_label]

            series = dated.set_index("invoice_date")["total_amount"].resample(freq).sum()
            if cumulative:
                series = series.cumsum()
            series = series.reset_index()
            series.columns = ["date", "revenue"]

            fig = area_chart(
                series, "date", "revenue",
                f"Chiffre d'affaires ({freq_label.lower()}{', cumulé' if cumulative else ''})",
                420,
            )
            st.plotly_chart(fig, **FW)

        with card():
            card_header(
                "Quand les clients achètent-ils ?",
                "Chiffre d'affaires par jour de la semaine et par heure.",
            )
            heat = dated.assign(
                jour=dated["invoice_date"].dt.day_name(),
                heure=dated["invoice_date"].dt.hour,
            )
            pivot = heat.pivot_table(
                index="jour", columns="heure", values="total_amount", aggfunc="sum"
            ).fillna(0)
            order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            pivot = pivot.reindex([d for d in order if d in pivot.index])
            fig = px.imshow(
                pivot, aspect="auto", color_continuous_scale=SCALE_HEAT,
                labels=dict(x="Heure", y="", color="CA (£)"),
            )
            fig.update_traces(
                hovertemplate="%{y}, %{x}h<br>CA : %{z:,.0f} £<extra></extra>",
                xgap=2, ygap=2,
            )
            fig.update_xaxes(dtick=1)
            fig.update_coloraxes(colorbar=dict(thickness=10, len=.8))
            st.plotly_chart(style_fig(fig, 340), **FW)

# ---- Transactions
with tab_table:
    with card():
        h1, h2 = st.columns([3, 1])
        with h1:
            card_header("Transactions", f"{len(df):,} transactions affichées")
        with h2:
            st.download_button(
                "Télécharger les transactions filtrées",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="retail_transactions.csv",
                mime="text/csv",
                **FW,
            )
        st.dataframe(
            df, hide_index=True, height=480,
            column_config={
                "total_amount": st.column_config.ProgressColumn(
                    "Montant (£)", format="%.2f",
                    min_value=0, max_value=float(df["total_amount"].max()),
                ),
                "invoice_date": st.column_config.DatetimeColumn(
                    "Date", format="DD/MM/YYYY HH:mm"
                ),
            },
            **FW,
        )

st.caption("FlowMind AI | Retail Analytics Dashboard | Données historiques du dataset Online Retail")

# ==========================================
# Prévision du chiffre d'affaires sur 7 jours
# ==========================================
st.divider()
st.markdown(
    '<div id="forecast"></div>'
    '<div class="fc-banner"><h2>Prévision du chiffre d\'affaires</h2>'
    "<p>Projection du chiffre d'affaires quotidien par apprentissage automatique. "
    "Une baseline est comparée aux modèles Random Forest et Gradient Boosting via l'erreur "
    "absolue moyenne (MAE) : plus elle est faible, plus l'erreur moyenne de prévision est petite.</p></div>",
    unsafe_allow_html=True,
)

with card():
    card_header("Paramètres de la prévision")
    forecast_days = st.slider(
        "Horizon de prévision (jours)",
        min_value=1,
        max_value=7,
        value=7,
    )
    run_forecast = st.button("Lancer la prévision", type="primary")

if run_forecast:
    try:
        response = requests.get(
            f"{API_URL}/analytics/forecast",
            params={"days": forecast_days},
            timeout=120,
        )
        response.raise_for_status()
        # Le résultat est conservé pour qu'il reste affiché après un téléchargement ou un changement de filtre
        st.session_state["forecast"] = response.json()
    except requests.RequestException as error:
        st.session_state.pop("forecast", None)
        st.error(f"Erreur lors de la prévision : {error}")

result = st.session_state.get("forecast")
if result is None:
    st.info("Choisissez un horizon puis lancez la prévision pour afficher le chiffre d'affaires prévisionnel.")
else:
    try:
        evaluation = result["evaluation"]
        forecast_df = pd.DataFrame(result["forecast"])
        forecast_df["date"] = pd.to_datetime(forecast_df["date"])
        forecast_df = forecast_df.set_index("date")

        # Période historique vs période prévue
        fc_first = forecast_df.index.min().strftime("%Y-%m-%d")
        fc_last = forecast_df.index.max().strftime("%Y-%m-%d")
        st.markdown(
            '<div class="timeline">'
            f'<div class="tl-block tl-hist"><b>Données historiques</b>'
            f"{result['data_from']} → {result['data_through']}</div>"
            f'<div class="tl-block tl-fc"><b>Prévision ({len(forecast_df)} j)</b>'
            f"{fc_first} → {fc_last}</div></div>",
            unsafe_allow_html=True,
        )

        # MAE (la plus faible est signalée)
        maes = [
            ("MAE — Baseline", evaluation["baseline_mae"]),
            ("MAE — Random Forest", evaluation["random_forest_mae"]),
            ("MAE — Gradient Boosting", evaluation["gradient_boosting_mae"]),
        ]
        lowest = min(value for _, value in maes)
        for column, (label, value) in zip(st.columns(3), maes):
            is_best = value == lowest
            tag = '<span class="mae-tag">Erreur la plus faible</span>' if is_best else ""
            column.markdown(
                f'<div class="mae{" best" if is_best else ""}">'
                f'<div class="mae-label"><span>{label}</span>{tag}</div>'
                f'<div class="mae-value">{value:,.2f} £</div></div>',
                unsafe_allow_html=True,
            )

        # Graphique du CA prévisionnel
        with card():
            card_header(
                "Chiffre d'affaires prévisionnel",
                "La ligne en pointillés et la zone ombrée correspondent aux valeurs prédites.",
            )
            show_history = st.toggle(
                "Superposer le CA observé des transactions chargées", value=False,
                help="Contexte uniquement : utilise les transactions actuellement chargées dans le "
                     "tableau de bord, qui peuvent ne pas couvrir toute la période historique.",
            )

            fc_plot = forecast_df.reset_index()
            fig = go.Figure()

            if show_history:
                hist = (
                    df_all.dropna(subset=["invoice_date"])
                    .assign(date=lambda d: d["invoice_date"].dt.normalize())
                    .groupby("date", as_index=False)["total_amount"].sum()
                )
                fig.add_trace(go.Scatter(
                    x=hist["date"], y=hist["total_amount"], mode="lines",
                    name="Observé (transactions chargées)",
                    line=dict(color=SLATE, width=2),
                    hovertemplate="Observé : %{y:,.0f} £<extra></extra>",
                ))

            x0 = (fc_plot["date"].min() - pd.Timedelta(hours=12)).to_pydatetime()
            x1 = (fc_plot["date"].max() + pd.Timedelta(hours=12)).to_pydatetime()
            fig.add_vrect(x0=x0, x1=x1, fillcolor="rgba(15,118,110,.07)", line_width=0, layer="below")
            fig.add_trace(go.Scatter(
                x=fc_plot["date"], y=fc_plot["predicted_revenue"], mode="lines+markers",
                name="CA prévu",
                line=dict(color=PRIMARY, width=2.5, dash="dash"),
                marker=dict(size=9, color="white", line=dict(color=PRIMARY, width=2)),
                hovertemplate="Prévu : %{y:,.0f} £<extra></extra>",
            ))
            fig.add_annotation(
                x=x0, y=1, yref="paper", xanchor="left", yanchor="top", showarrow=False,
                text="Prévision", font=dict(color=PRIMARY, size=12),
            )
            fig.update_layout(hovermode="x unified", showlegend=True)
            fig.update_yaxes(title="CA (£)", tickformat=",.0f")
            fig.update_xaxes(title="")
            st.plotly_chart(style_fig(fig, 380), **FW)

        # Détail + export CSV
        with card():
            d1, d2 = st.columns([3, 1])
            with d1:
                card_header("Détail des prévisions")
            with d2:
                st.download_button(
                    "Télécharger les prévisions (CSV)",
                    data=forecast_df.to_csv().encode("utf-8"),
                    file_name="previsions_chiffre_affaires.csv",
                    mime="text/csv",
                    **FW,
                )
            st.dataframe(
                forecast_df,
                column_config={
                    "predicted_revenue": st.column_config.NumberColumn(
                        "CA prévu (£)", format="%.2f"
                    ),
                },
                **FW,
            )

    except (KeyError, ValueError) as error:
        st.error(f"Erreur dans les résultats reçus : {error}")