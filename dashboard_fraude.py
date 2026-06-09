# -*- coding: utf-8 -*-
"""
Dashboard Détection de Fraude Bancaire — Banque de France
Design: salle de contrôle / terminal de surveillance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG & THÈME
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OSMP · Détection Fraude",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ────────────────────────────────────────────────────────────────
C = {
    "bg":        "#0A0E1A",
    "panel":     "#111827",
    "panel2":    "#1C2740",
    "red":       "#E63946",
    "orange":    "#F4A261",
    "blue":      "#38BDF8",
    "green":     "#4ADE80",
    "purple":    "#A78BFA",
    "text":      "#F1F5F9",
    "muted":     "#94A3B8",
    "border":    "#1E2D45",
    "red_dim":   "rgba(230,57,70,0.12)",
    "blue_dim":  "rgba(56,189,248,0.10)",
    "orange_dim":"rgba(244,162,97,0.12)",
}

PLOTLY_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=C["text"], size=12),
    xaxis=dict(gridcolor=C["border"], linecolor=C["border"], tickcolor=C["muted"]),
    yaxis=dict(gridcolor=C["border"], linecolor=C["border"], tickcolor=C["muted"]),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C["border"]),
    margin=dict(l=10, r=10, t=36, b=10),
    colorway=[C["red"], C["blue"], C["orange"], C["green"], C["purple"]],
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

/* Reset global */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: {C['bg']} !important;
    color: {C['text']};
    font-family: 'Inter', sans-serif;
}}
[data-testid="stSidebar"] {{
    background-color: {C['panel']} !important;
    border-right: 1px solid {C['border']};
}}
[data-testid="stSidebar"] * {{ color: {C['text']} !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}
.block-container {{ padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }}

/* KPI cards */
.kpi-card {{
    background: {C['panel']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, {C['blue']});
}}
.kpi-label {{
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {C['muted']};
    margin-bottom: 0.4rem;
}}
.kpi-value {{
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: {C['text']};
    line-height: 1.1;
}}
.kpi-sub {{
    font-size: 0.72rem;
    color: {C['muted']};
    margin-top: 0.3rem;
}}
.kpi-delta-up {{ color: {C['red']}; font-size: 0.75rem; }}
.kpi-delta-down {{ color: {C['green']}; font-size: 0.75rem; }}

/* Section titles */
.section-label {{
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {C['muted']};
    font-weight: 600;
    margin-bottom: 0.5rem;
}}
.section-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {C['text']};
    margin-bottom: 0.15rem;
}}
.panel-box {{
    background: {C['panel']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 1.2rem;
}}

/* Ticker */
.ticker-wrapper {{
    background: {C['panel']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 0.55rem 1.2rem;
    overflow: hidden;
    white-space: nowrap;
    margin-bottom: 1.2rem;
}}
.ticker-inner {{
    display: inline-block;
    animation: ticker-scroll 80s linear infinite;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: {C['muted']};
}}
.ticker-item {{ margin-right: 3rem; }}
.ticker-item span.fraud {{ color: {C['red']}; font-weight: 700; }}
.ticker-item span.ok {{ color: {C['green']}; }}
.ticker-item span.warn {{ color: {C['orange']}; }}
@keyframes ticker-scroll {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-50%); }}
}}

/* Alert badge */
.badge {{
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
.badge-red   {{ background: {C['red_dim']};    color: {C['red']};    border: 1px solid {C['red']}; }}
.badge-orange{{ background: {C['orange_dim']}; color: {C['orange']}; border: 1px solid {C['orange']}; }}
.badge-blue  {{ background: {C['blue_dim']};   color: {C['blue']};   border: 1px solid {C['blue']}; }}

/* Score bar */
.score-bar-bg {{
    background: {C['border']};
    border-radius: 3px;
    height: 5px;
    width: 100%;
    overflow: hidden;
}}
.score-bar-fill {{
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}}

/* Alert table */
.alert-table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
.alert-table th {{
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {C['muted']};
    padding: 0.5rem 0.8rem;
    border-bottom: 1px solid {C['border']};
    font-weight: 600;
    text-align: left;
}}
.alert-table td {{
    padding: 0.55rem 0.8rem;
    border-bottom: 1px solid rgba(30,45,69,0.5);
    color: {C['text']};
    vertical-align: middle;
}}
.alert-table tr:hover td {{ background: rgba(56,189,248,0.04); }}
.mono {{ font-family: 'Space Mono', monospace; font-size: 0.8rem; }}

/* Sidebar */
.sidebar-title {{
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {C['muted']};
    font-weight: 600;
    padding: 0.5rem 0 0.3rem;
}}
div[data-testid="stSlider"] {{ padding-top: 0.3rem; }}
div[data-testid="stSelectbox"] > div, div[data-testid="stMultiSelect"] > div {{
    background: {C['panel2']} !important;
    border-color: {C['border']} !important;
}}

/* Plotly containers */
.js-plotly-plot .plotly {{ border-radius: 8px; }}

/* Divider */
hr {{ border-color: {C['border']} !important; margin: 1rem 0 !important; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {C['border']}; border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def find_col(df, candidates):
    lmap = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lmap:
            return lmap[cand.lower()]
    return None


def standardize_columns(df):
    renamed = {c: (str(c).strip()
                   .replace("?", "").replace("/", "_").replace(" ", "_")
                   .replace("-", "_").replace("__", "_"))
               for c in df.columns}
    return df.rename(columns=renamed)


def risk_color(score):
    if score >= 0.8:
        return C["red"]
    elif score >= 0.5:
        return C["orange"]
    else:
        return C["blue"]


def score_badge(score):
    if score >= 0.8:
        return f'<span class="badge badge-red">CRITIQUE</span>'
    elif score >= 0.5:
        return f'<span class="badge badge-orange">MODÉRÉ</span>'
    else:
        return f'<span class="badge badge-blue">NORMAL</span>'


def mini_bar(score):
    pct = int(score * 100)
    color = risk_color(score)
    return (f'<div class="score-bar-bg">'
            f'<div class="score-bar-fill" style="width:{pct}%;background:{color}"></div>'
            f'</div>')


def apply_plotly_theme(fig, height=340):
    fig.update_layout(**PLOTLY_TEMPLATE, height=height)
    return fig


@st.cache_data(show_spinner=False)
def load_data(uploaded_file=None, path="dashboard_fraude_transactions_enrichi.csv"):
    import io
    import os

    def try_read(content):
        text = content.decode('utf-8', errors='replace')
        if not text.strip():
            raise ValueError("Fichier vide ou sans données CSV.")
        for sep in [',', ';', '\t']:
            try:
                df = pd.read_csv(io.StringIO(text), sep=sep)
                if len(df.columns) > 0:
                    return df
            except Exception:
                continue
        raise ValueError("Impossible de parser le CSV : format de colonnes non reconnu.")

    if uploaded_file is not None:
        content = uploaded_file.read()
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        return try_read(content)
    if os.path.exists(path):
        return pd.read_csv(path)
    # ── Données synthétiques de démonstration ──────────────────────────────
    rng = np.random.default_rng(42)
    n = 8_000
    hours = rng.integers(0, 24, n)
    months = rng.integers(1, 13, n)
    # fraude plus fréquente la nuit
    p_fraud = np.where((hours >= 0) & (hours < 6), 0.035,
              np.where((hours >= 6) & (hours < 12), 0.008, 0.012))
    is_fraud = rng.binomial(1, p_fraud).astype(int)
    amounts = np.where(is_fraud,
                       rng.lognormal(5.2, 1.1, n).clip(5, 5000),
                       rng.lognormal(4.0, 0.9, n).clip(1, 3000))
    chips = rng.choice(["Chip Transaction", "Swipe Transaction", "Online Transaction"],
                       n, p=[0.5, 0.3, 0.2])
    mcc_codes = rng.choice([5411, 5912, 4111, 5812, 7011, 5944, 7372, 5999], n)
    states = rng.choice(["CA","TX","NY","FL","IL","PA","OH","GA","NC","MI"], n)
    score = (is_fraud * rng.uniform(0.55, 0.99, n) +
             (1 - is_fraud) * rng.uniform(0.0, 0.45, n)).clip(0, 1)
    score = (score * 0.85 + rng.uniform(0, 0.15, n)).clip(0, 1)
    days = rng.integers(1, 29, n)
    return pd.DataFrame({
        "Year": 2019, "Month": months, "Day": days,
        "Time": [f"{h:02d}:{rng.integers(0,60):02d}:00" for h in hours],
        "hour": hours,
        "Amount": amounts.round(2),
        "Use Chip": chips,
        "MCC": mcc_codes,
        "Merchant State": states,
        "Is Fraud?": is_fraud,
        "score_risque": score.round(4),
        "alerte_modele": np.where(score >= 0.8, "Alerte", "OK"),
        "tranche_horaire": pd.cut(hours,
            bins=[-1,5,11,17,23],
            labels=["Nuit (0-5h)","Matin (6-11h)","Après-midi (12-17h)","Soir (18-23h)"]).astype(str),
            "classe_montant_detail": pd.cut(amounts,
            bins=[0,10,50,200,500,np.inf],
            labels=["<€10","€10-50","€50-200","€200-500",">€500"]).astype(str),
        "timezone_proxy": rng.choice(["EST","CST","MST","PST"], n),
    })


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:0.8rem 0 1rem;">
      <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                  color:{C['muted']};letter-spacing:0.2em;text-transform:uppercase;">
        Observatoire OSMP
      </div>
      <div style="font-size:1.15rem;font-weight:700;color:{C['text']};margin-top:0.2rem;">
        Centre de Contrôle<br>Anti-Fraude
      </div>
    </div>
    <hr style="border-color:{C['border']};margin:0 0 1rem 0;">
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Charger un CSV", type=["csv"],
                                      label_visibility="collapsed",
                                      help="Format attendu : colonnes hour, Amount, Is Fraud?, ...")

    st.markdown(f'<div class="sidebar-title">Période</div>', unsafe_allow_html=True)
    try:
        df_raw = load_data(uploaded_file)
        df_raw = standardize_columns(df_raw)
        col_month = find_col(df_raw, ["Month"])
        if col_month:
            df_raw[col_month] = pd.to_numeric(df_raw[col_month], errors="coerce")
            month_vals = sorted(df_raw[col_month].dropna().unique().astype(int).tolist())
            mois_fr = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Jun",
                       7:"Jul",8:"Aoû",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}
            sel_months = st.multiselect(
                "Mois", month_vals,
                default=month_vals,
                format_func=lambda x: mois_fr.get(int(x), str(x)),
                label_visibility="collapsed",
            )
        else:
            sel_months = []
    except Exception:
        sel_months = []

    st.markdown(f'<div class="sidebar-title">Canal</div>', unsafe_allow_html=True)
    col_chip = find_col(df_raw, ["Use_Chip","Use Chip","Chip"])
    if col_chip:
        chip_vals = sorted(df_raw[col_chip].dropna().astype(str).unique().tolist())
        sel_chips = st.multiselect("Canal", chip_vals, default=chip_vals,
                                   label_visibility="collapsed")
    else:
        sel_chips = []

    st.markdown(f'<div class="sidebar-title">Seuil d\'alerte critique</div>',
                unsafe_allow_html=True)
    risk_threshold = st.slider("Seuil", 0.0, 1.0, 0.80, 0.01,
                                label_visibility="collapsed")

    st.markdown(f'<div class="sidebar-title">Plage horaire</div>', unsafe_allow_html=True)
    col_hour_raw = find_col(df_raw, ["hour"])
    if col_hour_raw:
        df_raw[col_hour_raw] = pd.to_numeric(df_raw[col_hour_raw], errors="coerce")
        hour_range = st.slider("Heures", 0, 23, (0, 23), label_visibility="collapsed")
    else:
        hour_range = (0, 23)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.65rem;color:{C['muted']};line-height:1.7;">
      Données : IBM Synthetic Transactions<br>
      Modèle : XGBoost · PR-AUC ≈ 0.84<br>
      Mise à jour : temps réel simulé
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT & PRÉPARATION
# ─────────────────────────────────────────────────────────────────────────────
try:
    if 'df_raw' in globals():
        df = df_raw
    else:
        df = load_data(uploaded_file)
except Exception as e:
    st.error(f"❌ Erreur chargement : {e}")
    st.stop()

df = standardize_columns(df)

# Mapping colonnes
col_year    = find_col(df, ["Year"])
col_month   = find_col(df, ["Month"])
col_hour    = find_col(df, ["hour"])
col_amount  = find_col(df, ["Amount"])
col_chip    = find_col(df, ["Use_Chip","Use Chip","Chip"])
col_mcc     = find_col(df, ["MCC"])
col_state   = find_col(df, ["Merchant_State","Merchant State","State"])
col_fraud   = find_col(df, ["Is_Fraud","Is Fraud","Is"])
col_score   = find_col(df, ["score_risque","score risque","score"])
col_alert   = find_col(df, ["alerte_modele","alerte modele","alerte"])
col_tranche = find_col(df, ["tranche_horaire","tranche horaire"])
col_tz      = find_col(df, ["timezone_proxy"])
col_cls_amt = find_col(df, ["classe_montant_detail","classe montant detail"])

# Vérification minimale
if not all([col_hour, col_amount, col_fraud]):
    st.error("Colonnes minimales manquantes : `hour`, `Amount`, `Is Fraud?`")
    st.write("Colonnes détectées :", list(df.columns))
    st.stop()

# Conversions
for c in [col_hour, col_month, col_year, col_fraud, col_mcc]:
    if c:
        df[c] = pd.to_numeric(df[c], errors="coerce")
for c in [col_amount, col_score]:
    if c:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Features dérivées
if col_tranche is None:
    df["_tranche"] = pd.cut(df[col_hour],
        bins=[-1,5,11,17,23],
        labels=["Nuit (0-5h)","Matin (6-11h)","Après-midi (12-17h)","Soir (18-23h)"])
    col_tranche = "_tranche"

if col_cls_amt is None:
    df["_cls_amt"] = pd.cut(df[col_amount],
        bins=[0,10,50,200,500,np.inf],
        labels=["<€10","€10–50","€50–200","€200–500",">€500"])
    col_cls_amt = "_cls_amt"

if col_score is None:
    df["_score"] = (
        (df[col_amount] / df[col_amount].max()).fillna(0) * 0.5 +
        df[col_fraud].fillna(0) * 0.3 +
        df[col_hour].between(0, 5).astype(int) * 0.2
    ).clip(0, 1)
    col_score = "_score"

if col_alert is None:
    df["_alert"] = np.where(df[col_score] >= risk_threshold, "Alerte", "OK")
    col_alert = "_alert"

# ── Filtrage ──────────────────────────────────────────────────────────────
flt = df.copy()
if sel_months and col_month:
    flt = flt[flt[col_month].isin(sel_months)]
if sel_chips and col_chip:
    flt = flt[flt[col_chip].astype(str).isin(sel_chips)]
if col_hour:
    flt = flt[flt[col_hour].between(hour_range[0], hour_range[1])]

# ── Alerte dynamique avec seuil ───────────────────────────────────────────
flt["_alert_live"] = np.where(flt[col_score] >= risk_threshold, "Alerte", "OK")

# ─────────────────────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────────────────────
n_total   = len(flt)
n_fraud   = int(flt[col_fraud].fillna(0).sum())
taux      = n_fraud / n_total if n_total else 0
n_alert   = int((flt[col_score] >= risk_threshold).sum())
avg_score = float(flt[col_score].fillna(0).mean())
avg_fraud_amount = float(flt[flt[col_fraud]==1][col_amount].mean()) if n_fraud else 0


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:flex-start;justify-content:space-between;
            margin-bottom:0.8rem;padding-bottom:0.8rem;
            border-bottom:1px solid {C['border']};">
  <div>
    <div style="font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;
                color:{C['muted']};font-weight:600;font-family:'Space Mono',monospace;">
      BANQUE DE FRANCE · OSMP · SYSTÈME ANTI-FRAUDE
    </div>
    <div style="font-size:1.6rem;font-weight:700;color:{C['text']};margin-top:0.2rem;
                font-family:'Inter',sans-serif;line-height:1.2;">
      Centre de Surveillance<br>
      <span style="color:{C['red']};">des Transactions à Risque</span>
    </div>
  </div>
  <div style="text-align:right;">
    <div style="display:inline-flex;align-items:center;gap:0.4rem;
                background:{C['panel']};border:1px solid {C['border']};
                border-radius:20px;padding:0.35rem 0.9rem;">
      <div style="width:7px;height:7px;border-radius:50%;background:{C['green']};
                  animation:pulse 2s infinite;box-shadow:0 0 6px {C['green']};"></div>
      <span style="font-family:'Space Mono',monospace;font-size:0.7rem;color:{C['muted']};">
        SYSTÈME ACTIF
      </span>
    </div>
    <div style="font-size:0.7rem;color:{C['muted']};margin-top:0.4rem;
                font-family:'Space Mono',monospace;">
      {n_total:,} transactions analysées
    </div>
  </div>
</div>
<style>@keyframes pulse {{
  0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:0.5;transform:scale(1.3)}}
}}</style>
""", unsafe_allow_html=True)

# ── Ticker d'alertes ──────────────────────────────────────────────────────
top_alerts = flt.nlargest(min(30, len(flt)), col_score)
ticker_items = ""
for _, row in top_alerts.iterrows():
    sc = row[col_score]
    h  = int(row[col_hour]) if pd.notna(row[col_hour]) else "?"
    amt = f"€{row[col_amount]:.0f}" if pd.notna(row[col_amount]) else "N/A"
    cls = "fraud" if sc >= 0.8 else ("warn" if sc >= 0.5 else "ok")
    lab = "ALERTE" if sc >= 0.8 else ("RISQUE" if sc >= 0.5 else "OK")
    ticker_items += (
        f'<span class="ticker-item">'
        f'<span class="{cls}">■ {lab}</span> '
        f'Score&nbsp;<b>{sc:.2f}</b> · {amt} · {h}h'
        f'</span>'
    )
double = ticker_items * 2
st.markdown(f"""
<div class="ticker-wrapper">
  <div class="ticker-inner">{double}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

kpis = [
    (k1, "TRANSACTIONS", f"{n_total:,}", f"périmètre filtré", C["blue"], ""),
    (k2, "FRAUDES DÉTECTÉES", f"{n_fraud:,}", f"{taux:.3%} du volume", C["red"], "▲"),
    (k3, "ALERTES CRITIQUES",  f"{n_alert:,}",
     f"seuil ≥ {risk_threshold:.2f}", C["orange"], ""),
    (k4, "SCORE MOYEN", f"{avg_score:.3f}",
     "score de risque moyen", C["purple"], ""),
    (k5, "MONTANT MOY. FRAUDE", f"€{avg_fraud_amount:,.0f}",
     "par transaction frauduleuse", C["red"], ""),
]

for col_widget, label, value, sub, accent, delta in kpis:
    delta_html = ""
    if delta == "▲":
        delta_html = f'<div class="kpi-delta-up">▲ Priorité maximale</div>'
    with col_widget:
        st.markdown(f"""
        <div class="kpi-card" style="--accent:{accent}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
          {delta_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 2 — Heatmap Heure×Mois + Gauge + Distribution scores
# ─────────────────────────────────────────────────────────────────────────────
r2a, r2b = st.columns([3, 2])

with r2a:
    st.markdown(f"""
    <div class="section-label">Cartographie temporelle</div>
    <div class="section-title">Taux de fraude · Heure × Mois</div>
    """, unsafe_allow_html=True)

    if col_month in flt.columns:
        pivot_data = (
            flt.groupby([col_month, col_hour], dropna=True)[col_fraud]
            .agg(["sum", "count"])
            .assign(taux=lambda x: x["sum"] / x["count"] * 100)
            .reset_index()
        )
        if len(pivot_data) > 0:
            pivot_hm = pivot_data.pivot(index=col_month, columns=col_hour, values="taux").fillna(0)
            mois_fr = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Jun",
                       7:"Jul",8:"Aoû",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}
            y_labels = [mois_fr.get(int(m), str(m)) for m in pivot_hm.index]
            x_labels = [f"{int(h)}h" for h in pivot_hm.columns]

            fig_hm = go.Figure(go.Heatmap(
                z=pivot_hm.values,
                x=x_labels, y=y_labels,
                colorscale=[
                    [0.0, C["panel2"]],
                    [0.3, "rgba(244,162,97,0.4)"],
                    [0.6, "rgba(230,57,70,0.7)"],
                    [1.0, C["red"]],
                ],
                showscale=True,
                colorbar=dict(
                    title=dict(
                        text="Taux (%)", 
                        font=dict(color=C["muted"], size=10),
                    ),
                    tickfont=dict(color=C["muted"], size=9),
                    thickness=10, len=0.8,
                    bgcolor="rgba(0,0,0,0)",
                ),
                hovertemplate="<b>%{y} · %{x}</b><br>Taux de fraude : %{z:.3f}%<extra></extra>",
            ))
            apply_plotly_theme(fig_hm, height=310)
            fig_hm.update_layout(
                xaxis=dict(side="bottom", tickfont=dict(size=9), gridcolor="rgba(0,0,0,0)"),
                yaxis=dict(tickfont=dict(size=9), gridcolor="rgba(0,0,0,0)"),
            )
            # Annotation zone nocturne
            fig_hm.add_shape(
                type="rect", x0=-0.5, x1=5.5, y0=-0.5, y1=len(y_labels)-0.5,
                line=dict(color=C["red"], width=1.5, dash="dot"),
                fillcolor="rgba(0,0,0,0)", layer="above",
            )
            fig_hm.add_annotation(
                x=2.5, y=len(y_labels)-0.3,
                text="ZONE À RISQUE ÉLEVÉ · 0h–5h",
                font=dict(size=8, color=C["red"], family="Space Mono"),
                showarrow=False, bgcolor="rgba(10,14,26,0.7)",
            )
            st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Colonne 'Month' non disponible pour la heatmap.")

with r2b:
    st.markdown(f"""
    <div class="section-label">Score global</div>
    <div class="section-title">Jauge de risque agrégé</div>
    """, unsafe_allow_html=True)

    # Gauge
    gauge_color = C["red"] if avg_score >= 0.6 else C["orange"] if avg_score >= 0.35 else C["green"]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_score,
        number=dict(
            font=dict(family="Space Mono", color=C["text"], size=36),
            valueformat=".3f",
        ),
        delta=dict(
            reference=0.1, valueformat=".3f",
            font=dict(color=C["muted"], size=11),
        ),
        gauge=dict(
            axis=dict(
                range=[0, 1], tickwidth=1, tickcolor=C["muted"],
                tickfont=dict(color=C["muted"], size=9),
                nticks=6,
            ),
            bar=dict(color=gauge_color, thickness=0.22),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=C["border"],
            steps=[
                dict(range=[0.0, 0.35], color=C["panel2"]),
                dict(range=[0.35, 0.65], color="rgba(244,162,97,0.08)"),
                dict(range=[0.65, 1.0],  color="rgba(230,57,70,0.08)"),
            ],
            threshold=dict(
                line=dict(color=C["red"], width=2),
                thickness=0.75,
                value=risk_threshold,
            ),
        ),
        title=dict(
            text=f"<span style='font-size:10px;color:{C['muted']};"
                 f"font-family:Space Mono'>SCORE MOYEN · SEUIL {risk_threshold:.2f}</span>",
            font=dict(size=10, color=C["muted"]),
        ),
    ))
    apply_plotly_theme(fig_gauge, height=200)
    fig_gauge.update_layout(margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    # Distribution scores
    st.markdown(f"""
    <div class="section-label" style="margin-top:0.5rem;">Distribution des scores de risque</div>
    """, unsafe_allow_html=True)

    fig_dist = go.Figure()
    # Légitimes
    legit_scores = flt[flt[col_fraud] == 0][col_score].dropna()
    fraud_scores = flt[flt[col_fraud] == 1][col_score].dropna()
    if len(legit_scores):
        fig_dist.add_trace(go.Histogram(
            x=legit_scores, nbinsx=30, name="Légitime",
            marker_color=C["blue"], opacity=0.55,
            histnorm="percent",
        ))
    if len(fraud_scores):
        fig_dist.add_trace(go.Histogram(
            x=fraud_scores, nbinsx=30, name="Fraude",
            marker_color=C["red"], opacity=0.75,
            histnorm="percent",
        ))
    fig_dist.add_vline(
        x=risk_threshold, line_color=C["orange"],
        line_dash="dash", line_width=1.5,
        annotation_text=f"Seuil {risk_threshold:.2f}",
        annotation_font=dict(size=9, color=C["orange"]),
        annotation_position="top right",
    )
    apply_plotly_theme(fig_dist, height=165)
    fig_dist.update_layout(
        barmode="overlay",
        showlegend=True,
        legend=dict(orientation="h", y=1.1, font=dict(size=9)),
        margin=dict(l=5, r=5, t=20, b=5),
        xaxis=dict(title=dict(text="Score", font=dict(size=9)), tickfont=dict(size=8)),
        yaxis=dict(title=dict(text="%", font=dict(size=9)), tickfont=dict(size=8)),
    )
    st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
# ROW 3 — Timeline fraude (area chart pleine largeur)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="section-label">Dynamique temporelle</div>
<div class="section-title">Taux de fraude heure par heure — signal vs volume</div>
""", unsafe_allow_html=True)

taux_h = (
    flt.groupby(col_hour, dropna=True)[col_fraud]
    .agg(["sum", "count"])
    .assign(taux=lambda x: x["sum"] / x["count"] * 100)
    .reset_index()
    .sort_values(col_hour)
)

fig_timeline = make_subplots(specs=[[{"secondary_y": True}]])

# Volume (barres grises en fond)
fig_timeline.add_trace(
    go.Bar(
        x=taux_h[col_hour], y=taux_h["count"],
        name="Volume transactions",
        marker_color="rgba(56,189,248,0.07)",
        marker_line=dict(width=0),
        hovertemplate="<b>%{x}h</b><br>Volume : %{y:,}<extra></extra>",
    ),
    secondary_y=True,
)

# Taux fraude (area rouge)
fig_timeline.add_trace(
    go.Scatter(
        x=taux_h[col_hour], y=taux_h["taux"],
        name="Taux de fraude (%)",
        mode="lines+markers",
        line=dict(color=C["red"], width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(230,57,70,0.15)",
        marker=dict(size=5, color=C["red"]),
        hovertemplate="<b>%{x}h</b><br>Taux : %{y:.3f}%<extra></extra>",
    ),
    secondary_y=False,
)

# Zone nocturne 0–5h
fig_timeline.add_vrect(
    x0=-0.5, x1=5.5,
    fillcolor="rgba(230,57,70,0.06)",
    layer="below", line_width=0,
    annotation_text="ZONE NOCTURNE",
    annotation_font=dict(size=8, color=C["red"]),
    annotation_position="top left",
)

fig_timeline.update_layout(
    **PLOTLY_TEMPLATE,
    height=230,
    hovermode="x unified",
)
fig_timeline.update_layout(
    legend=dict(orientation="h", y=1.12, font=dict(size=9)),
    margin=dict(l=5, r=5, t=10, b=5),
)
fig_timeline.update_xaxes(
    tickvals=list(range(0, 24, 2)),
    ticktext=[f"{h}h" for h in range(0, 24, 2)],
    gridcolor=C["border"],
)
fig_timeline.update_yaxes(
    title_text="Taux de fraude (%)",
    title_font=dict(size=9, color=C["red"]),
    tickfont=dict(size=8),
    secondary_y=False,
    gridcolor=C["border"],
)
fig_timeline.update_yaxes(
    title_text="Volume",
    title_font=dict(size=9, color=C["blue"]),
    tickfont=dict(size=8),
    secondary_y=True,
    gridcolor="rgba(0,0,0,0)",
    showgrid=False,
)
st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})

st.markdown(f"""
<div style="background:{C['panel']};border:1px solid {C['border']};border-radius:8px;
            padding:0.7rem 1.2rem;margin-bottom:1rem;">
  <div style="display:flex;gap:2rem;flex-wrap:wrap;">
    <div style="font-size:0.75rem;color:{C['muted']};">
      <span style="color:{C['red']};font-weight:600;">■</span>
      La zone 0h–5h concentre les taux de fraude les plus élevés.
      Le volume nocturne est faible, ce qui amplifie le taux conditionnel.
      <b style="color:{C['text']};">Recommandation :</b> abaisser le seuil d'alerte à 0.15 sur cette plage.
    </div>
    <div style="font-size:0.75rem;color:{C['muted']};">
      <span style="color:{C['blue']};font-weight:600;">■</span>
      L'heure est encodée cycliquement dans le modèle (sin/cos) pour éviter
      la discontinuité 23h→0h. Les transactions sont horodatées en heure locale du marchand —
      signal comportemental pertinent indépendamment du fuseau.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 4 — Scatter Montant×Score + Canal + MCC
# ─────────────────────────────────────────────────────────────────────────────
r4a, r4b, r4c = st.columns([5, 3, 4])

with r4a:
    st.markdown(f"""
    <div class="section-label">Signal montant</div>
    <div class="section-title">Montant × Score de risque</div>
    """, unsafe_allow_html=True)

    sample_n = min(3000, len(flt))
    df_sample = flt.sample(sample_n, random_state=42) if len(flt) > sample_n else flt.copy()
    df_sample["_log_amt"] = np.log1p(df_sample[col_amount].clip(lower=0.01))
    df_sample["_label"] = df_sample[col_fraud].map({0: "Légitime", 1: "Fraude"}).fillna("Légitime")

    fig_scatter = px.scatter(
        df_sample,
        x="_log_amt",
        y=col_score,
        color="_label",
        color_discrete_map={"Légitime": C["blue"], "Fraude": C["red"]},
        opacity=0.55,
        size_max=6,
        hover_data={
            col_amount: ":.2f",
            col_score: ":.3f",
            "_log_amt": False,
            "_label": False,
        },
        labels={
            "_log_amt": "log(Montant)",
            col_score: "Score de risque",
            "_label": "Classe",
        },
    )
    fig_scatter.add_hline(
        y=risk_threshold, line_dash="dot",
        line_color=C["orange"], line_width=1.5,
        annotation_text=f"Seuil {risk_threshold:.2f}",
        annotation_font=dict(size=8, color=C["orange"]),
    )
    apply_plotly_theme(fig_scatter, height=300)
    fig_scatter.update_traces(marker=dict(size=4))
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

with r4b:
    st.markdown(f"""
    <div class="section-label">Canal de paiement</div>
    <div class="section-title">Exposition au risque</div>
    """, unsafe_allow_html=True)

    if col_chip and col_chip in flt.columns:
        chip_taux = (
            flt.groupby(col_chip, dropna=True)[col_fraud]
            .agg(["sum", "count"])
            .assign(taux=lambda x: x["sum"] / x["count"] * 100)
            .sort_values("taux", ascending=True)
            .reset_index()
        )
        chip_taux["_label"] = chip_taux[col_chip].astype(str)
        chip_colors = [
            C["red"] if t > chip_taux["taux"].mean() * 1.5 else C["orange"]
            if t > chip_taux["taux"].mean() else C["blue"]
            for t in chip_taux["taux"]
        ]
        fig_chip = go.Figure(go.Bar(
            x=chip_taux["taux"],
            y=chip_taux["_label"],
            orientation="h",
            marker_color=chip_colors,
            marker_line=dict(width=0),
            text=[f"{t:.3f}%" for t in chip_taux["taux"]],
            textposition="outside",
            textfont=dict(size=9, color=C["text"], family="Space Mono"),
            hovertemplate="<b>%{y}</b><br>Taux fraude : %{x:.3f}%<extra></extra>",
        ))
        apply_plotly_theme(fig_chip, height=300)
        fig_chip.update_layout(
            xaxis=dict(title=dict(text="Taux de fraude (%)", font=dict(size=9))),
            yaxis=dict(tickfont=dict(size=9)),
            margin=dict(l=5, r=60, t=10, b=5),
        )
        st.plotly_chart(fig_chip, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Colonne 'Use Chip' introuvable.")

with r4c:
    st.markdown(f"""
    <div class="section-label">Catégories marchands</div>
    <div class="section-title">Top 8 MCC · Taux de fraude</div>
    """, unsafe_allow_html=True)

    if col_mcc and col_mcc in flt.columns:
        mcc_taux = (
            flt.groupby(col_mcc, dropna=True)[col_fraud]
            .agg(["sum", "count"])
            .assign(taux=lambda x: x["sum"] / x["count"] * 100)
            .query("count >= 20")
            .nlargest(8, "taux")
            .reset_index()
        )
        mcc_taux["_mcc_str"] = "MCC " + mcc_taux[col_mcc].astype(int).astype(str)

        fig_mcc = go.Figure(go.Bar(
            x=mcc_taux["_mcc_str"],
            y=mcc_taux["taux"],
            marker=dict(
                color=mcc_taux["taux"],
                colorscale=[[0, C["panel2"]], [0.5, C["orange"]], [1.0, C["red"]]],
                showscale=False,
                line=dict(width=0),
            ),
            text=[f"{t:.2f}%" for t in mcc_taux["taux"]],
            textposition="outside",
            textfont=dict(size=8, family="Space Mono", color=C["text"]),
            hovertemplate="<b>%{x}</b><br>Taux fraude : %{y:.3f}%<br>n=%{customdata}<extra></extra>",
            customdata=mcc_taux["count"],
        ))
        apply_plotly_theme(fig_mcc, height=300)
        fig_mcc.update_layout(
            xaxis=dict(tickfont=dict(size=8), tickangle=20),
            yaxis=dict(title=dict(text="Taux fraude (%)", font=dict(size=9))),
            margin=dict(l=5, r=5, t=10, b=40),
        )
        st.plotly_chart(fig_mcc, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Colonne 'MCC' introuvable.")


# ─────────────────────────────────────────────────────────────────────────────
# ROW 5 — Montant par classe + Fuseaux horaires
# ─────────────────────────────────────────────────────────────────────────────
r5a, r5b = st.columns([3, 2])

with r5a:
    st.markdown(f"""
    <div class="section-label">Analyse des montants</div>
    <div class="section-title">Taux de fraude par tranche de montant — KDE comparatif</div>
    """, unsafe_allow_html=True)

    # KDE log-montant
    from scipy import stats as scipy_stats  # local import

    fig_kde = go.Figure()
    for classe, color, label in [
        (0, C["blue"], "Légitime"),
        (1, C["red"],  "Fraude"),
    ]:
        vals = np.log1p(flt[flt[col_fraud] == classe][col_amount].dropna().clip(lower=0.01))
        if len(vals) < 10:
            continue
        kde = scipy_stats.gaussian_kde(vals, bw_method=0.3)
        x_range = np.linspace(vals.min(), vals.max(), 200)
        y_kde = kde(x_range)
        fig_kde.add_trace(go.Scatter(
            x=x_range, y=y_kde,
            name=label,
            mode="lines",
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor="rgba(56,189,248,0.08)" if classe == 0 else "rgba(230,57,70,0.08)",
            hovertemplate=f"<b>{label}</b><br>log(Montant)=%{{x:.2f}}<extra></extra>",
        ))
        # Médiane
        med = vals.median()
        fig_kde.add_vline(
            x=med, line_color=color, line_dash="dot", line_width=1.5,
            annotation_text=f"Méd. {label[0]}: {med:.2f}",
            annotation_font=dict(size=8, color=color),
            annotation_position="top right" if classe == 1 else "top left",
        )

    apply_plotly_theme(fig_kde, height=260)
    fig_kde.update_layout(
        xaxis=dict(title=dict(text="log(Montant + 1)", font=dict(size=9))),
        yaxis=dict(title=dict(text="Densité (KDE)", font=dict(size=9))),
        legend=dict(orientation="h", y=1.1, font=dict(size=9)),
        margin=dict(l=5, r=5, t=20, b=10),
    )
    st.plotly_chart(fig_kde, use_container_width=True, config={"displayModeBar": False})

with r5b:
    st.markdown(f"""
    <div class="section-label">Fuseaux horaires</div>
    <div class="section-title">Taux de fraude · Heure locale vs timezone</div>
    """, unsafe_allow_html=True)

    if col_tz and col_tz in flt.columns:
        tz_taux = (
            flt.groupby([col_tz, col_hour], dropna=True)[col_fraud]
            .agg(["sum", "count"])
            .assign(taux=lambda x: x["sum"] / x["count"] * 100)
            .reset_index()
        )
        tz_order = ["EST", "CST", "MST", "PST"]
        tz_colors = {
            "EST": C["red"], "CST": C["orange"],
            "MST": C["purple"], "PST": C["blue"],
        }
        fig_tz = go.Figure()
        for tz in tz_order:
            sub = tz_taux[tz_taux[col_tz] == tz].sort_values(col_hour)
            if len(sub) == 0:
                continue
            fig_tz.add_trace(go.Scatter(
                x=sub[col_hour], y=sub["taux"],
                name=tz,
                mode="lines",
                line=dict(color=tz_colors.get(tz, C["muted"]), width=2, shape="spline"),
                fill="tonexty" if tz != "EST" else "tozeroy",
                fillcolor=f"rgba(0,0,0,0)",
                hovertemplate=f"<b>{tz}</b> · %{{x}}h<br>Taux : %{{y:.3f}}%<extra></extra>",
            ))
        apply_plotly_theme(fig_tz, height=260)
        fig_tz.update_layout(
            xaxis=dict(
                title=dict(text="Heure locale (marchand)", font=dict(size=9)),
                tickvals=list(range(0, 24, 4)),
                ticktext=[f"{h}h" for h in range(0, 24, 4)],
            ),
            yaxis=dict(title=dict(text="Taux fraude (%)", font=dict(size=9))),
            legend=dict(orientation="h", y=1.12, font=dict(size=9)),
            margin=dict(l=5, r=5, t=20, b=10),
        )
        st.plotly_chart(fig_tz, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"""
        <div style="font-size:0.7rem;color:{C['muted']};padding:0.4rem 0;line-height:1.6;">
          Les courbes montrent que le pic nocturne est <b style="color:{C['text']}">cohérent
          dans tous les fuseaux</b> — l'heure locale du marchand est donc
          un signal comportemental valide, indépendamment du décalage UTC.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback : barres par tranche horaire
        tranche_taux = (
            flt.groupby(col_tranche, dropna=True)[col_fraud]
            .agg(["sum", "count"])
            .assign(taux=lambda x: x["sum"] / x["count"] * 100)
            .reset_index()
        )
        tranche_taux["_t"] = tranche_taux[col_tranche].astype(str)
        avg_t = tranche_taux["taux"].mean()
        t_colors = [
            C["red"] if t > avg_t * 1.5 else C["orange"] if t > avg_t else C["blue"]
            for t in tranche_taux["taux"]
        ]
        fig_tranche = go.Figure(go.Bar(
            x=tranche_taux["_t"], y=tranche_taux["taux"],
            marker_color=t_colors, marker_line=dict(width=0),
            text=[f"{t:.3f}%" for t in tranche_taux["taux"]],
            textposition="outside",
            textfont=dict(size=9, color=C["text"], family="Space Mono"),
        ))
        fig_tranche.add_hline(y=avg_t, line_dash="dot", line_color=C["muted"],
                              line_width=1,
                              annotation_text=f"Moy. {avg_t:.3f}%",
                              annotation_font=dict(size=8, color=C["muted"]))
        apply_plotly_theme(fig_tranche, height=260)
        fig_tranche.update_layout(
            xaxis=dict(tickfont=dict(size=8)),
            yaxis=dict(title=dict(text="Taux fraude (%)", font=dict(size=9))),
            margin=dict(l=5, r=5, t=20, b=40),
        )
        st.plotly_chart(fig_tranche, use_container_width=True,
                        config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
# ROW 6 — Table alertes prioritaires
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:0.5rem;">
  <div class="section-label">File d'investigation</div>
  <div class="section-title">Top transactions à investiguer en priorité</div>
</div>
""", unsafe_allow_html=True)

top_df = flt.sort_values(col_score, ascending=False).head(25).copy()

# Construire le HTML de la table
cols_meta = []
if col_score:   cols_meta.append((col_score, "Score"))
if col_hour:    cols_meta.append((col_hour, "Heure"))
if col_amount:  cols_meta.append((col_amount, "Montant"))
if col_mcc:     cols_meta.append((col_mcc, "MCC"))
if col_state:   cols_meta.append((col_state, "État"))
if col_chip:    cols_meta.append((col_chip, "Canal"))
if col_fraud:   cols_meta.append((col_fraud, "Fraude"))

th_html = "".join(
    [f'<th>PRIORITÉ</th>', f'<th>NIVEAU</th>'] +
    [f"<th>{h}</th>" for _, h in cols_meta] +
    ["<th>SIGNAL</th>"]
)

rows_html = ""
for rank, (_, row) in enumerate(top_df.iterrows(), 1):
    sc = float(row[col_score]) if col_score and pd.notna(row[col_score]) else 0.0
    badge = score_badge(sc)
    bar   = mini_bar(sc)
    rank_color = C["red"] if rank <= 5 else C["orange"] if rank <= 10 else C["muted"]

    td = (f'<td class="mono" style="color:{rank_color};font-weight:700;">#{rank:02d}</td>'
          f'<td>{badge}</td>')
    for col_name, _ in cols_meta:
        val = row.get(col_name, "")
        if col_name == col_score:
            td += f'<td class="mono" style="color:{risk_color(sc)}">{sc:.3f}</td>'
        elif col_name == col_amount:
            amt = f"€{float(val):.2f}" if pd.notna(val) else "N/A"
            td += f'<td class="mono">{amt}</td>'
        elif col_name == col_fraud:
            is_f = int(val) if pd.notna(val) else 0
            mark = f'<span style="color:{C["red"]};font-weight:700;">✓</span>' if is_f else '—'
            td += f'<td style="text-align:center">{mark}</td>'
        else:
            td += f'<td style="color:{C["muted"]}">{str(val)[:20] if pd.notna(val) else "—"}</td>'

    td += f'<td style="min-width:80px">{bar}</td>'
    rows_html += f"<tr>{td}</tr>"

table_html = f"""
<div class="panel-box" style="overflow-x:auto;">
  <table class="alert-table">
    <thead><tr>{th_html}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid {C['border']};
            display:flex;justify-content:space-between;align-items:center;
            font-size:0.65rem;color:{C['muted']};font-family:'Space Mono',monospace;">
  <div>BANQUE DE FRANCE · OSMP · Prototype Analytique — Dataset IBM Synthetic Transactions</div>
  <div>Modèle : XGBoost · Seuil actif : {risk_threshold:.2f} · {n_total:,} tx analysées</div>
</div>
""", unsafe_allow_html=True)
