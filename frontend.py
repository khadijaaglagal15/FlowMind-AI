import requests
import pandas as pd
import plotly.express as px
import streamlit as st

API_URL = "http://127.0.0.1:8000"

# Palette : teal profond, ambre, prune, menthe
TEAL = "#0F4C5C"
AMBER = "#E9A23B"
PLUM = "#6D3B6E"
MINT = "#5FB49C"
CORAL = "#E4572E"
INK = "#1B2A33"
SOFT = "#F4F7F7"

SEQUENCE = [TEAL, AMBER, PLUM, MINT, CORAL, "#3E7CB1", "#A3B18A", "#B5838D"]
SCALE_TEAL = ["#D6ECE8", MINT, TEAL]

st.set_page_config(
    page_title="FlowMind AI - Retail Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- Style (CSS)
st.markdown(
    f"""
    <style>
    .block-container {{ padding-top: 1.5rem; max-width: 1400px; }}

    .hero {{
        background: linear-gradient(120deg, {TEAL} 0%, #1B6B73 55%, {MINT} 100%);
        border-radius: 18px;
        padding: 28px 34px;
        color: white;
        margin-bottom: 1.2rem;
    }}
    .hero h1 {{ margin: 0; font-size: 2.2rem; color: black; }}
    .hero p  {{ margin: 6px 0 0 0; opacity: .9; font-size: 1.05rem; }}

    [data-testid="stMetric"] {{
        background: blue;
        border: 1px solid #E3EAEA;
        border-left: 6px solid {TEAL};
        border-radius: 14px;
        padding: 14px 18px;
        box-shadow: 0 2px 8px rgba(15, 76, 92, .06);
    }}
    div[data-testid="column"]:nth-child(2) [data-testid="stMetric"] {{ border-left-color: {AMBER}; }}
    div[data-testid="column"]:nth-child(3) [data-testid="stMetric"] {{ border-left-color: {PLUM}; }}
    div[data-testid="column"]:nth-child(4) [data-testid="stMetric"] {{ border-left-color: {MINT}; }}
    div[data-testid="column"]:nth-child(5) [data-testid="stMetric"] {{ border-left-color: {CORAL}; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        background: {SOFT};
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background: {TEAL};
        color: black !important;
    }}

    .insight {{
        background: #FFF6E5;
        border-left: 5px solid {AMBER};
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0 14px 0;
        color: {INK};
    }}
    .badge-ok  {{ background:#E3F5EE; color:#12805C; padding:4px 12px; border-radius:20px; font-weight:600; }}
    .badge-ko  {{ background:#FDE8E4; color:{CORAL}; padding:4px 12px; border-radius:20px; font-weight:600; }}
    </style>
    """,
    unsafe_allow_html=True,
)


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


def style_fig(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=INK),
        margin=dict(l=10, r=10, t=50, b=10),
        title_font_size=18,
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E8EEEE")
    return fig


# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    st.markdown("## 📊 FlowMind AI")
    backend_ok = check_backend()
    if backend_ok:
        st.markdown('<span class="badge-ok">● Backend connecté</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-ko">● Backend indisponible</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### Données")
    limit = st.select_slider(
        "Nombre de transactions à charger",
        options=[100, 500, 1000, 5000],
        value=1000,
    )
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if not backend_ok:
    st.markdown(
        '<div class="hero"><h1>📊 FlowMind AI</h1>'
        "<p>Retail Intelligence & Analytics</p></div>",
        unsafe_allow_html=True,
    )
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
    st.markdown("### Filtres")

    countries = sorted(df_all["country"].dropna().unique())
    selected_countries = st.multiselect("Pays", countries, placeholder="Tous les pays")

    search = st.text_input("🔎 Produit", placeholder="ex : LANTERN")

    if df_all["invoice_date"].notna().any():
        min_date = df_all["invoice_date"].min().date()
        max_date = df_all["invoice_date"].max().date()
        date_range = st.date_input(
            "Période", value=(min_date, max_date), min_value=min_date, max_value=max_date
        )
    else:
        date_range = None

df = df_all.copy()
if selected_countries:
    df = df[df["country"].isin(selected_countries)]
if search:
    df = df[df["description"].str.contains(search, case=False, na=False)]
if date_range and len(date_range) == 2:
    start, end = date_range
    df = df[
        df["invoice_date"].dt.date.between(start, end) | df["invoice_date"].isna()
    ]

# ------------------------------------------------------------------ En-tête
st.markdown(
    """
    <div class="hero">
        <h1>📊 FlowMind AI</h1>
        <p>Analysez les transactions, repérez les meilleurs produits
        et comparez les performances par pays.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("Aucune transaction ne correspond aux filtres choisis.")
    st.stop()

# KPI (calculés sur les données filtrées)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Transactions", f"{len(df):,}")
k2.metric("Chiffre d'affaires", f"{df['total_amount'].sum():,.0f} £")
k3.metric("Transaction moyenne", f"{df['total_amount'].mean():,.2f} £")
k4.metric("Produits distincts", f"{df['description'].nunique():,}")
k5.metric("Pays", f"{df['country'].nunique():,}")

st.caption(
    f"Vue basée sur {len(df):,} transactions filtrées "
    f"(sur {len(df_all):,} chargées depuis l'API)."
)

# ------------------------------------------------------------------ Onglets
tab_home, tab_products, tab_countries, tab_time, tab_table = st.tabs(
    ["🏠 Vue d'ensemble", "🏆 Produits", "🌍 Pays", "📅 Évolution", "🧾 Transactions"]
)

# ---- Vue d'ensemble
with tab_home:
    st.subheader("Indicateurs globaux du dataset")
    st.caption("Calculés par le backend sur l'ensemble des données, sans filtre.")
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
            with st.container(border=True):
                st.markdown("#### 🏆 Produit le plus vendu")
                if best:
                    st.markdown(f"**{best['product']}**")
                    st.metric("Quantité vendue", f"{best['quantity_sold']:,}")
                else:
                    st.info("Aucun produit disponible.")
        with c2:
            with st.container(border=True):
                st.markdown("#### 🌍 Pays avec le plus de revenus")
                if top:
                    st.markdown(f"**{top['country']}**")
                    st.metric("Chiffre d'affaires", f"{top['revenue']:,.2f} £")
                else:
                    st.info("Aucun pays disponible.")
    except requests.RequestException as error:
        st.error(f"Impossible de charger les statistiques : {error}")
    except (KeyError, ValueError) as error:
        st.error(f"Erreur dans les données reçues : {error}")

    st.divider()
    left, right = st.columns([3, 2])
    with left:
        by_day = (
            df.dropna(subset=["invoice_date"])
            .assign(date=lambda d: d["invoice_date"].dt.date)
            .groupby("date", as_index=False)["total_amount"].sum()
        )
        fig = px.area(
            by_day, x="date", y="total_amount",
            title="Chiffre d'affaires par jour",
            color_discrete_sequence=[TEAL],
            labels={"date": "", "total_amount": "CA (£)"},
        )
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)
    with right:
        share = df.groupby("country")["total_amount"].sum().nlargest(6).reset_index()
        fig = px.pie(
            share, names="country", values="total_amount", hole=0.55,
            title="Répartition du CA (top 6 pays)",
            color_discrete_sequence=SEQUENCE,
        )
        fig.update_traces(textinfo="percent", pull=[0.04] + [0] * 5)
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

# ---- Produits
with tab_products:
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
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(style_fig(fig, 80 + top_n * 32), use_container_width=True)

    leader = products.iloc[-1]
    st.markdown(
        f'<div class="insight">💡 <b>{leader["description"]}</b> arrive en tête '
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
    view = st.radio("Affichage", ["Carte", "Barres", "Treemap"], horizontal=True)

    if view == "Carte":
        fig = px.choropleth(
            by_country, locations="country", locationmode="country names",
            color="revenue", hover_data=["transactions", "average"],
            color_continuous_scale=SCALE_TEAL,
            title="Chiffre d'affaires par pays",
        )
        fig.update_geos(showframe=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(style_fig(fig, 480), use_container_width=True)
    elif view == "Barres":
        top_c = by_country.nlargest(10, "revenue").sort_values("revenue")
        fig = px.bar(
            top_c, x="revenue", y="country", orientation="h",
            color="revenue", color_continuous_scale=SCALE_TEAL,
            title="Top 10 des pays par chiffre d'affaires",
            labels={"revenue": "CA (£)", "country": ""},
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig, 460), use_container_width=True)
    else:
        fig = px.treemap(
            by_country, path=["country"], values="revenue",
            color="average", color_continuous_scale=SCALE_TEAL,
            title="Poids de chaque pays (couleur = transaction moyenne)",
        )
        st.plotly_chart(style_fig(fig, 480), use_container_width=True)

    st.dataframe(
        by_country.sort_values("revenue", ascending=False),
        use_container_width=True, hide_index=True,
        column_config={
            "country": "Pays",
            "revenue": st.column_config.NumberColumn("CA (£)", format="%.0f"),
            "transactions": "Transactions",
            "average": st.column_config.NumberColumn("Moyenne (£)", format="%.2f"),
        },
    )

# ---- Évolution
with tab_time:
    dated = df.dropna(subset=["invoice_date"])
    if dated.empty:
        st.info("Aucune date exploitable dans les données.")
    else:
        c1, c2 = st.columns([2, 1])
        freq_label = c1.radio("Regrouper par", ["Jour", "Semaine", "Mois"], horizontal=True)
        cumulative = c2.toggle("Cumul")
        freq = {"Jour": "D", "Semaine": "W", "Mois": "MS"}[freq_label]

        series = dated.set_index("invoice_date")["total_amount"].resample(freq).sum()
        if cumulative:
            series = series.cumsum()
        series = series.reset_index()
        series.columns = ["date", "revenue"]

        fig = px.line(
            series, x="date", y="revenue", markers=True,
            title=f"Chiffre d'affaires ({freq_label.lower()}{', cumulé' if cumulative else ''})",
            color_discrete_sequence=[PLUM],
            labels={"date": "", "revenue": "CA (£)"},
        )
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)

        st.markdown("#### Quand les clients achètent-ils ?")
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
            pivot, aspect="auto", color_continuous_scale=["#FFF6E5", AMBER, CORAL],
            labels=dict(x="Heure", y="", color="CA (£)"),
        )
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

# ---- Transactions
with tab_table:
    st.caption(f"{len(df):,} transactions affichées")
    st.dataframe(
        df, use_container_width=True, hide_index=True, height=480,
        column_config={
            "total_amount": st.column_config.ProgressColumn(
                "Montant (£)", format="%.2f",
                min_value=0, max_value=float(df["total_amount"].max()),
            ),
            "invoice_date": st.column_config.DatetimeColumn(
                "Date", format="DD/MM/YYYY HH:mm"
            ),
        },
    )
    st.download_button(
        "📥 Télécharger les transactions filtrées",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="retail_transactions.csv",
        mime="text/csv",
    )

st.divider()
st.caption("FlowMind AI | Retail Analytics Dashboard | Données historiques du dataset Online Retail")

# ==========================================
# Prévision du chiffre d'affaires sur 7 jours
# ==========================================

st.divider()
st.header("🔮 Prévision du chiffre d'affaires")

forecast_days = st.slider(
    "Horizon de prévision (jours)",
    min_value=1,
    max_value=7,
    value=7,
)

if st.button("Lancer la prévision"):
    try:
        response = requests.get(
            f"{API_URL}/analytics/forecast",
            params={"days": forecast_days},
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()

        st.caption(
            f"Données historiques : {result['data_from']} "
            f"→ {result['data_through']}"
        )

        evaluation = result["evaluation"]

        col1, col2, col3 = st.columns(3)
        col1.metric(
            "MAE — Baseline",
            f"{evaluation['baseline_mae']:,.2f} £",
        )
        col2.metric(
            "MAE — Random Forest",
            f"{evaluation['random_forest_mae']:,.2f} £",
        )
        col3.metric(
            "MAE — Gradient Boosting",
            f"{evaluation['gradient_boosting_mae']:,.2f} £",
        )

        forecast_df = pd.DataFrame(result["forecast"])
        forecast_df["date"] = pd.to_datetime(forecast_df["date"])
        forecast_df = forecast_df.set_index("date")

        st.subheader("📈 Chiffre d'affaires prévisionnel")
        st.line_chart(forecast_df["predicted_revenue"])

        st.subheader("📋 Détail des prévisions")
        st.dataframe(forecast_df, use_container_width=True)

        st.download_button(
            "📥 Télécharger les prévisions (CSV)",
            data=forecast_df.to_csv().encode("utf-8"),
            file_name="previsions_chiffre_affaires.csv",
            mime="text/csv",
        )

    except requests.RequestException as error:
        st.error(f"Erreur lors de la prévision : {error}")
    except (KeyError, ValueError) as error:
        st.error(f"Erreur dans les résultats reçus : {error}")
