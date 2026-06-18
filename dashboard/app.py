"""
CPI Nowcaster Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os

st.set_page_config(
    page_title="CPI Nowcaster | Real-Time Inflation",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quantico:wght@400;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
/* ---- RESET & BASE ---- */
#MainMenu, footer, header { visibility: hidden; }

:root {
    --brand:              #BBF351;
    --brand-softer:       #0D1A02;
    --brand-soft:         #1A3306;
    --border-brand:       #BBF351;
    --border-brand-sub:   #2D4A0F;
    --border-default:     #1A1A1A;
    --border-subtle:      #0D0D0D;
    --bg-primary:         #000000;
    --bg-secondary:       #0A0A0A;
    --bg-card:            #000000;
    --bg-card-hover:      #111111;
    --text-heading:       #F0F0F0;
    --text-body:          #A0A0A0;
    --text-subtle:        #707070;
    --shadow-xs:          0 1px 2px 0 rgb(0 0 0 / 0.2);
    --shadow-md:          0 4px 6px -1px rgb(0 0 0 / 0.3), 0 0 10px -2px rgba(187, 243, 81, 0.06);
    --shadow-lg:          0 10px 15px -3px rgb(0 0 0 / 0.3), 0 0 15px -4px rgba(187, 243, 81, 0.08);
}

.stApp {
    background: #000000;
    background-image:
        radial-gradient(ellipse at 15% 15%, rgba(187, 243, 81, 0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 85%, rgba(187, 243, 81, 0.02) 0%, transparent 50%);
}

/* ---- TYPOGRAPHY ---- */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Quantico', sans-serif !important;
    color: var(--text-heading) !important;
    font-weight: 700 !important;
    letter-spacing: 0.2px !important;
}

p, span, div, li, a {
    font-family: 'Inter', sans-serif !important;
}

/* ---- CARD ---- */
.card {
    background: #000000;
    border: 2px solid #1A1A1A;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.2);
}

.card-interactive {
    transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
    cursor: pointer;
}

.card-interactive:hover {
    background: #111111;
    border-color: #BBF351;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3), 0 0 10px -2px rgba(187, 243, 81, 0.06);
}

/* ---- NAVBAR ---- */
.navbar {
    background: #000000;
    border-bottom: 1px solid #1A1A1A;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -16px -16px 24px -16px;
}

.nav-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.nav-orb {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #BBF351;
    box-shadow: 0 0 20px rgba(187, 243, 81, 0.4), 0 0 60px rgba(187, 243, 81, 0.15);
}

.nav-title {
    font-family: 'Quantico', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: #F0F0F0;
    letter-spacing: 0.2px;
}

.nav-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    color: #707070;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #BBF351;
    box-shadow: 0 0 8px rgba(187, 243, 81, 0.6);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ---- HERO ---- */
.hero-metric {
    font-family: 'Quantico', sans-serif;
    font-weight: 700;
    font-size: 5rem;
    color: #BBF351;
    line-height: 1;
    letter-spacing: 0.2px;
    text-shadow: 0 0 80px rgba(187, 243, 81, 0.25);
}

.hero-label {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #707070;
    font-weight: 600;
}

/* ---- STAT ---- */
.stat-value {
    font-family: 'Quantico', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    color: #BBF351;
    line-height: 1;
}

.stat-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #707070;
    font-weight: 600;
    margin-top: 6px;
}

/* ---- DATA ROW ---- */
.data-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 11px 0;
    border-bottom: 1px solid #0D0D0D;
    transition: background 0.15s;
}

.data-row:last-child { border-bottom: none; }

.data-row:hover {
    background: rgba(187, 243, 81, 0.03);
    border-radius: 6px;
    padding: 11px 8px;
}

.data-label   { color: #A0A0A0; font-size: 0.83rem; }
.data-value   { color: #F0F0F0; font-weight: 600; font-size: 0.83rem; }
.data-brand   { color: #BBF351; font-weight: 700; font-size: 0.83rem; }

/* ---- SECTION TITLE ---- */
.section-title {
    font-family: 'Quantico', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: #F0F0F0;
    letter-spacing: 0.2px;
    margin-bottom: 4px;
}

.section-subtitle {
    font-size: 0.8rem;
    color: #707070;
    margin-bottom: 0;
}

/* ---- ICON SHAPE ---- */
.icon-shape {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    margin-bottom: 12px;
}

.icon-brand  { background: #0D1A02; color: #BBF351; border: 1px solid #2D4A0F; }
.icon-purple { background: rgba(191, 90, 242, 0.08); color: #BF5AF2; border: 1px solid rgba(191, 90, 242, 0.2); }
.icon-cyan   { background: rgba(0, 229, 255, 0.06); color: #00E5FF; border: 1px solid rgba(0, 229, 255, 0.15); }

/* ---- BADGE ---- */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid;
    font-family: 'Inter', sans-serif;
}

.badge-brand   { background: #0D1A02; border-color: #2D4A0F; color: #D4F785; }
.badge-success { background: #001A12; border-color: #003D2E; color: #00FF99; }
.badge-danger  { background: #1A0008; border-color: #4D001A; color: #FF6688; }
.badge-neutral { background: #111111; border-color: #222222; color: #F0F0F0; }

/* ---- FOOTER ---- */
.footer {
    border-top: 1px solid #1A1A1A;
    padding-top: 24px;
    margin-top: 48px;
}

/* ---- OVERRIDES ---- */
.stPlotlyChart { border-radius: 8px; }
div[data-testid="stVerticalBlock"] { gap: 0; }
</style>
""", unsafe_allow_html=True)

# ---- DATA ----
@st.cache_data(ttl=60)
def load_nowcast():
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "nowcast.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return None

nowcast = load_nowcast()

# ---- NAVBAR ----
date_str = nowcast['date'] if nowcast else 'No data'
st.markdown(f"""
<div class="navbar">
    <div class="nav-logo">
        <div class="nav-orb"></div>
        <span class="nav-title">CPI Nowcaster</span>
    </div>
    <div class="nav-status">
        <div class="status-dot"></div>
        <span>Live &bull; {date_str}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- MAIN ----
if nowcast and nowcast.get("nowcast") is not None:

    delta_val = (nowcast['nowcast'] - nowcast.get('latest_actual', 0)
                 if nowcast.get('latest_actual') else 0)
    delta_str = f"+{delta_val:.2f}%" if delta_val >= 0 else f"{delta_val:.2f}%"
    delta_color = "#BBF351" if delta_val >= 0 else "#FF6688"

    # ---- HERO ----
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 0 48px 0;">
        <p class="hero-label">Current CPI Inflation Nowcast</p>
        <p class="hero-metric">{nowcast['nowcast']:.2f}%</p>
        <p style="color: {delta_color}; font-weight: 600; font-size: 1rem; margin-top: 8px;">
            {delta_str} vs latest official
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- STATS ----
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <p class="stat-value">{nowcast.get('latest_actual', 0):.2f}%</p>
            <p class="stat-label">Latest Official CPI</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <p class="stat-value">{nowcast['rmse_historical']:.2f}%</p>
            <p class="stat-label">Model RMSE</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <p class="stat-value">{nowcast['data_available']['training_samples']}</p>
            <p class="stat-label">Training Samples</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        m = nowcast['data_available']['monthly_series']
        d = nowcast['data_available']['daily_series']
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <p class="stat-value">{m}<span style="color:#707070;font-size:1.2rem;">+</span>{d}</p>
            <p class="stat-label">Data Series</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    # ---- CHART + PIPELINE ----
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Feature Importance</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Top drivers of the current nowcast</p>', unsafe_allow_html=True)

        if nowcast.get('top_features'):
            features_df = pd.DataFrame(nowcast['top_features'])

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=features_df['feature'][::-1],
                x=features_df['importance'][::-1],
                orientation='h',
                marker=dict(
                    color=features_df['importance'][::-1],
                    colorscale=[[0, 'rgba(187,243,81,0.15)'], [1, '#BBF351']],
                    line_width=0,
                ),
                text=[f"{v:.1%}" for v in features_df['importance'][::-1]],
                textposition='outside',
                textfont=dict(color='#707070', size=11),
                hovertemplate='%{y}: %{x:.1%}<extra></extra>'
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#A0A0A0',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, color='#F0F0F0',
                           tickfont=dict(family='Inter', size=12)),
                margin=dict(l=0, r=48, t=8, b=0),
                height=240,
                bargap=0.4,
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Data Pipeline</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Current snapshot</p>', unsafe_allow_html=True)
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        pipeline_rows = [
            ("Date",        nowcast['date'],                                     False),
            ("Monthly",     str(nowcast['data_available']['monthly_series']) + " series", True),
            ("Daily",       str(nowcast['data_available']['daily_series']) + " series",   True),
            ("Model",       "MIDAS + XGBoost",                                   False),
            ("Validation",  "Expanding Window CV",                               False),
            ("Automation",  "GitHub Actions (daily)",                            False),
            ("Deployment",  "Streamlit Cloud",                                   False),
        ]

        for label, value, highlight in pipeline_rows:
            val_class = "data-brand" if highlight else "data-value"
            st.markdown(f"""
            <div class="data-row">
                <span class="data-label">{label}</span>
                <span class="{val_class}">{value}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    # ---- METHODOLOGY ----
    st.markdown('<p class="section-title" style="margin-bottom: 16px;">How It Works</p>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="card card-interactive">
            <div class="icon-shape icon-brand">◈</div>
            <h4 style="margin: 0 0 8px 0;">Data Pipeline</h4>
            <p style="color: #A0A0A0; font-size: 0.82rem; line-height: 1.6; margin: 0;">
                Fetches 9 monthly macro indicators and 5 daily financial series from FRED,
                respecting actual publication release calendars.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card card-interactive">
            <div class="icon-shape icon-purple">◇</div>
            <h4 style="margin: 0 0 8px 0;">Ragged Edge Engine</h4>
            <p style="color: #A0A0A0; font-size: 0.82rem; line-height: 1.6; margin: 0;">
                Aligns mixed-frequency data without future-peeking. Handles publication lags
                and creates real-time feature snapshots for each reference month.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="card card-interactive">
            <div class="icon-shape icon-cyan">◎</div>
            <h4 style="margin: 0 0 8px 0;">MIDAS + XGBoost</h4>
            <p style="color: #A0A0A0; font-size: 0.82rem; line-height: 1.6; margin: 0;">
                MIDAS compresses daily data into monthly signals. XGBoost captures non-linear
                economic patterns, validated with time-series-safe expanding window CV.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ---- FOOTER ----
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #555555; font-size: 0.75rem;">
                Powered by FRED &bull; GitHub Actions &bull; Streamlit Cloud
            </span>
            <span style="color: #333333; font-size: 0.7rem;">&copy; 2026 CPI Nowcaster</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif nowcast and nowcast.get("error"):
    st.markdown(f"""
    <div style="background:#1A0008; border:1px solid #4D001A; border-radius:8px; padding:16px; margin-top:32px;">
        <p style="color:#FF6688; font-weight:600; margin:0 0 4px 0;">Pipeline Error</p>
        <p style="color:#A0A0A0; font-size:0.85rem; margin:0;">{nowcast['error']}</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="background:#0D1A02; border:1px solid #2D4A0F; border-radius:8px; padding:16px; margin-top:32px;">
        <p style="color:#BBF351; font-weight:600; margin:0 0 4px 0;">No Data</p>
        <p style="color:#A0A0A0; font-size:0.85rem; margin:0;">
            Run <code style="color:#BBF351;">python src/nowcast.py</code> to generate predictions.
        </p>
    </div>
    """, unsafe_allow_html=True)
