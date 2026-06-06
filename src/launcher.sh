#!/bin/bash

# Navigate to your project directory
cd "$HOME/projects/home_automation/src/" || exit 1

# --- Loop 1: Heating Control App ---
while true; do
    echo "[$(date)] Starting main.py..."
    python3 main.py
    echo "[$(date)] main.py crashed! Restarting in 5 seconds..."
    sleep 5
done &  # The '&' pushes this entire loop into the background

# --- Loop 2: Streamlit Dashboard ---
while true; do
    echo "[$(date)] Starting Streamlit..."
    # --server.headless=true prevents it from trying to open a browser window on the Pi
    python3 -m streamlit run streamlit_app.py --server.headless=true
    echo "[$(date)] Streamlit crashed! Restarting in 5 seconds..."
    sleep 5
done &  # The '&' pushes this loop into the background as well

# This keeps the main script alive and listening. 
# If you press Ctrl+C, it will propagate the signal to both background loops.
wait