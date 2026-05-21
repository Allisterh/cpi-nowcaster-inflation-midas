"""
CPI Nowcaster Dashboard
Interactive Streamlit app displaying real-time inflation nowcast.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="CPI Nowcaster",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 US CPI Inflation Nowcaster")
st.caption("Real-time estimate of current-month CPI inflation before official release")

# Load data
@st.cache_data(ttl=60)
def load_nowcast():
    """Load the latest nowcast from the JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "nowcast.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return None

nowcast = load_nowcast()

# ---- MAIN METRIC ----
if nowcast:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current Nowcast",
            value=f"{nowcast['nowcast']:.2f}%",
            delta=f"{nowcast['nowcast'] - nowcast['latest_actual']:.2f}% vs last actual" if nowcast['latest_actual'] else None
        )
    
    with col2:
        st.metric(
            label="Latest Official CPI",
            value=f"{nowcast['latest_actual']:.2f}%" if nowcast['latest_actual'] else "N/A"
        )
    
    with col3:
        st.metric(
            label="Model Accuracy (RMSE)",
            value=f"{nowcast['rmse_historical']:.2f}%"
        )

    st.divider()

    # ---- WHAT'S DRIVING THE NOWCAST ----
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔑 Top Drivers")
        if nowcast['top_features']:
            features_df = pd.DataFrame(nowcast['top_features'])
            fig = px.bar(
                features_df,
                x="importance",
                y="feature",
                orientation="h",
                title="Feature Importance",
                color="importance",
                color_continuous_scale="blues"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📋 Data Snapshot")
        st.write(f"**Date:** {nowcast['date']}")
        st.write(f"**Monthly series:** {nowcast['data_available']['monthly_series']}")
        st.write(f"**Daily series:** {nowcast['data_available']['daily_series']}")
        st.write(f"**Training samples:** {nowcast['data_available']['training_samples']}")
        st.write(f"**Model:** MIDAS + XGBoost")
        st.write(f"**Validation:** Expanding window CV")

    st.divider()

    # ---- HOW IT WORKS ----
    st.subheader("🛠️ How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1. Data Pipeline**
        - Fetches 5 monthly macro indicators (CPI, unemployment, etc.)
        - Fetches 3 daily financial indicators (breakeven rates, oil, dollar)
        - Respects actual publication calendars
        """)
    
    with col2:
        st.markdown("""
        **2. Ragged Edge Processing**
        - Aligns mixed-frequency data
        - Fills available data without peeking into the future
        - Creates real-time feature snapshots
        """)
    
    with col3:
        st.markdown("""
        **3. MIDAS + XGBoost Model**
        - MIDAS weights daily data into monthly signals
        - XGBoost captures non-linear patterns
        - Expanding window validation mimics real-time usage
        """)

    # ---- FOOTER ----
    st.divider()
    st.caption(f"Last updated: {nowcast['date']} • Runs daily via GitHub Actions • Data: FRED")

else:
    st.warning("No nowcast data found. Run the model first to generate predictions.")
    st.code("python src/nowcast.py", language="bash")