import streamlit as st
import requests
import base64
import json
import re
import os
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="Dual-Step AI Swing Trading Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .buy-signal {
        background-color: rgba(38, 166, 154, 0.15);
        border: 1px solid #26a69a;
        color: #26a69a;
        padding: 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.25rem;
        text-align: center;
    }
    .sell-signal {
        background-color: rgba(239, 83, 80, 0.15);
        border: 1px solid #ef5350;
        color: #ef5350;
        padding: 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.25rem;
        text-align: center;
    }
    .neutral-signal {
        background-color: rgba(255, 179, 0, 0.15);
        border: 1px solid #ffb300;
        color: #ffb300;
        padding: 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.25rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

if "step1_metrics" not in st.session_state:
    st.session_state["step1_metrics"] = ""
if "display_step1_metrics" not in st.session_state:
    st.session_state["display_step1_metrics"] = ""
if "extracted_price" not in st.session_state:
    st.session_state["extracted_price"] = 116.41
if "blueprint_data" not in st.session_state:
    st.session_state["blueprint_data"] = None

st.sidebar.title("🎛️ Display & Risk Controls")
view_mode = st.sidebar.radio(
    "🖥️ Screen View Mode",
    options=["🔲 Dual-Step View (Step 1 + Step 2)", "🎯 Fullscreen Focus: JEV AI Step 2 Only"],
    index=0
)
show_step1 = (view_mode == "🔲 Dual-Step View (Step 1 + Step 2)")
show_params = st.sidebar.checkbox("👁️ Show Sidebar Parameter Sliders", value=True)

api_key = ""
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
elif "OPENROUTER_API_KEY" in os.environ:
    api_key = os.environ["OPENROUTER_API_KEY"]

if show_params:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Trade Parameters")
    risk_reward_ratio = st.sidebar.slider("Risk-to-Reward Ratio (RRR)", 1.5, 4.0, 2.0, 0.1)
    trailing_stop_pct = st.sidebar.slider("Trailing Stop Percentage (%)", 1.0, 5.0, 2.0, 0.1)
    model_choice = st.sidebar.selectbox("OpenRouter AI Model", ["google/gemini-2.5-flash", "google/gemini-2.0-flash-001"], index=0)
else:
    risk_reward_ratio = 2.0
    trailing_stop_pct = 2.0
    model_choice = "google/gemini-2.5-flash"

st.title("📈 Dual-Step AI Swing Trading Assistant")
st.markdown("Multi-timeframe Vision AI extraction paired with JEV AI deterministic structured decision engine.")

# (For full code see requirements and app.py download tab)
