import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import time

# --- CONFIGURATION ---
LOG_FILE_PATH = "logs/history.log"

# --- STREAMLIT CONFIG & THEME ---
st.set_page_config(
    page_title="Solar Heating Monitor",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS injection
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        div[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: bold; }
        .stButton>button { width: 100%; border-radius: 4px; }
        /* Style the summary card wrapper */
        div[data-testid="stSubheader"] { margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=5)
def load_and_parse_log(file_path):
    """Reads JSON Lines log file and flattens it into an aggregated Pandas DataFrame."""
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    parsed_records = []
    
    with open(file_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                
                total_mppt_power = sum(mppt.get("power", 0) for mppt in data.get("mppts", []))
                total_inv_pin = sum(inv.get("p_in", 0) for inv in data.get("inverters", []))
                total_inv_pout = sum(inv.get("p_out", 0) for inv in data.get("inverters", []))
                
                record = {
                    "timestamp": pd.to_datetime(data.get("timestamp")),
                    "soc": data.get("battery", {}).get("soc", 0),
                    "relay_state": 1 if data.get("relay_state", False) else 0,
                    "mppt_power": total_mppt_power,
                    "inverter_in_power": total_inv_pin,
                    "inverter_out_power": total_inv_pout
                }
                parsed_records.append(record)
            except Exception:
                continue

    if not parsed_records:
        return pd.DataFrame()

    df = pd.DataFrame(parsed_records)
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    return df

# Helper to generate dark-themed static line plots
def create_static_chart(dataframe, y_columns, colors, is_area=False):
    """Generates a Plotly chart styled for dark backgrounds with touch interactions disabled."""
    if is_area:
        fig = px.area(dataframe, x=dataframe.index, y=y_columns, color_discrete_sequence=colors)
    else:
        fig = px.line(dataframe, x=dataframe.index, y=y_columns, color_discrete_sequence=colors)
        
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title=None, tickfont=dict(color='#888888')),
        yaxis=dict(showgrid=True, gridcolor='#22252a', title=None, tickfont=dict(color='#888888')),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='white')),
        margin=dict(l=10, r=10, t=10, b=10),
        height=260
    )
    # config={'staticPlot': True} disables mouse scaling, dragging, and touch trapping on mobile
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})


# --- MAIN APP FLOW ---
st.title("☀️ Solar Heating Status")

df = load_and_parse_log(LOG_FILE_PATH)

if df.empty:
    st.warning(f"Waiting for log data... Checked path: {os.path.abspath(LOG_FILE_PATH)}")
else:
    latest = df.iloc[-1]
    last_update_str = latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    # --- 1. TOP SUMMARY FRAME ---
    summary_container = st.container(border=True)
    with summary_container:
        # Puts status description and real-time metadata inside the framed container widget
        c_top1, c_top2 = st.columns([2, 1])
        with c_top1:
            st.subheader("Current Status")
        with c_top2:
            st.markdown(f"<p style='text-align: right; color: #888888; font-size: 0.9rem; margin-top: 10px;'>Last Update: {last_update_str}</p>", unsafe_allow_html=True)
            
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Current Production", value=f"{int(latest['mppt_power'])} W")
        with col2:
            st.metric(label="Current Consumption", value=f"{int(latest['inverter_out_power'])} W")
        with col3:
            st.metric(label="Battery SoC", value=f"{latest['soc']:.1f} %")
        with col4:
            relay_label = "🔥 HEATING ON" if latest['relay_state'] == 1 else "❄️ STANDBY"
            st.metric(label="Relay State", value=relay_label)
            
    st.markdown("---")

    # --- 2. TIME SCALE FILTER ---
    st.subheader("Historical Analytics")
    t_col1, t_col2, t_col3, _ = st.columns([1, 1, 1, 5])
    
    if "time_scale" not in st.session_state:
        st.session_state.time_scale = "24h"
        
    with t_col1:
        if st.button("Last 24 Hours", type="primary" if st.session_state.time_scale == "24h" else "secondary"):
            st.session_state.time_scale = "24h"
            st.rerun()
    with t_col2:
        if st.button("Last Week", type="primary" if st.session_state.time_scale == "7d" else "secondary"):
            st.session_state.time_scale = "7d"
            st.rerun()
    with t_col3:
        if st.button("Entire Log", type="primary" if st.session_state.time_scale == "all" else "secondary"):
            st.session_state.time_scale = "all"
            st.rerun()

    max_time = df['timestamp'].max()
    if st.session_state.time_scale == "24h":
        df_filtered = df[df['timestamp'] >= (max_time - timedelta(hours=24))]
    elif st.session_state.time_scale == "7d":
        df_filtered = df[df['timestamp'] >= (max_time - timedelta(days=7))]
    else:
        df_filtered = df

    df_chart = df_filtered.set_index("timestamp")

    # --- 3. GRAPH PLOTS ---
    
    # Plot 1: MPPT Solar Power
    st.markdown("#### ⚡ MPPT Power Production (Watts)")
    create_static_chart(df_chart, ["mppt_power"], ["#ffa500"])

    # Plot 2: Inverters In vs Out
    st.markdown("#### 🔄 Inverters Power (Input vs Output)")
    inv_chart_data = df_chart.rename(
        columns={"inverter_in_power": "Inverter Input (W)", "inverter_out_power": "Inverter Output (W)"}
    )
    create_static_chart(inv_chart_data, ["Inverter Input (W)", "Inverter Output (W)"], ["#2ca02c", "#d62728"])

    # Plot 3: Battery SoC
    st.markdown("#### 🔋 Battery State of Charge (%)")
    create_static_chart(df_chart, ["soc"], ["#1f77b4"], is_area=True)

    # Plot 4: Relay State
    st.markdown("#### 🔌 Heating Relay Control State")
    create_static_chart(df_chart, ["relay_state"], ["#ff7f0e"], is_area=True)

    # Bottom helper log counter
    st.caption(f"Total historical data intervals analyzed: {len(df_filtered)}")

# --- 4. AUTO REFRESH LOOP ---
time.sleep(60)      
st.rerun()