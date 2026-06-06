import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

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
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=5) # Cache data for 5 seconds to prevent hammering the SD card on user clicks
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
                
                # Extract and aggregate powers
                total_mppt_power = sum(mppt.get("power", 0) for mppt in data.get("mppts", []))
                total_inv_pin = sum(inv.get("p_in", 0) for inv in data.get("inverters", []))
                total_inv_pout = sum(inv.get("p_out", 0) for inv in data.get("inverters", []))
                
                record = {
                    "timestamp": pd.to_datetime(data.get("timestamp")),
                    "soc": data.get("battery", {}).get("soc", 0),
                    "relay_state": 1 if data.get("relay_state", False) else 0, # convert to numeric for easy plotting
                    "mppt_power": total_mppt_power,
                    "inverter_in_power": total_inv_pin,
                    "inverter_out_power": total_inv_pout
                }
                parsed_records.append(record)
            except Exception:
                continue # Skip broken lines safely

    if not parsed_records:
        return pd.DataFrame()

    df = pd.DataFrame(parsed_records)
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    return df

# --- MAIN APP FLOW ---
st.title("☀️ Solar Heating Command Center")

# Load data
df = load_and_parse_log(LOG_FILE_PATH)

if df.empty:
    st.warning(f"Waiting for log data... Checked path: {os.path.abspath(LOG_FILE_PATH)}")
    st.info("Ensure your main loop is generating records in JSON Lines format inside that file.")
else:
    # --- 1. TOP SUMMARY FRAME ---
    # Fetch latest record for real-time overview
    latest = df.iloc[-1]
    
    st.subheader("Current Status")
    summary_container = st.container(border=True)
    with summary_container:
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
    
    # Horizontal layout for selection buttons using st.columns
    t_col1, t_col2, t_col3, _ = st.columns([1, 1, 1, 5])
    
    # Track selection in session state
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

    # Apply data filtering based on selection
    max_time = df['timestamp'].max()
    if st.session_state.time_scale == "24h":
        df_filtered = df[df['timestamp'] >= (max_time - timedelta(hours=24))]
    elif st.session_state.time_scale == "7d":
        df_filtered = df[df['timestamp'] >= (max_time - timedelta(days=7))]
    else:
        df_filtered = df

    # Prepare index for clean chart plotting axes
    df_chart = df_filtered.set_index("timestamp")

    # --- 3. GRAPH PLOTS ---
    
    # Plot 1: MPPT Solar Power
    st.markdown("#### ⚡ MPPT Power Production (Watts)")
    st.line_chart(df_chart["mppt_power"], color="#ffa500")

    # Plot 2: Inverters In vs Out
    st.markdown("#### 🔄 Inverters Power (Input vs Output)")
    # Renaming for cleaner legends on the graph
    inv_chart_data = df_chart[["inverter_in_power", "inverter_out_power"]].rename(
        columns={"inverter_in_power": "Inverter Input (W)", "inverter_out_power": "Inverter Output (W)"}
    )
    st.line_chart(inv_chart_data, color=["#2ca02c", "#d62728"])

    # Plot 3: Battery SoC
    st.markdown("#### 🔋 Battery State of Charge (%)")
    st.area_chart(df_chart["soc"], color="#1f77b4")

    # Plot 4: Relay State
    st.markdown("#### 🔌 Heating Relay Control State")
    # Step-like area plot works beautifully for binary states
    st.area_chart(df_chart["relay_state"], color="#ff7f0e")

    # Bottom timestamp metadata
    st.caption(f"Showing records up to: {max_time.strftime('%Y-%m-%d %H:%M:%S')}. Total logged intervals viewed: {len(df_filtered)}")