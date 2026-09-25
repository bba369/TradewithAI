import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="Jev AI Swing Planner", page_icon="📈", layout="wide")
st.title("📈 Jev AI Pro Swing Trading Planner (Production Ready)")
st.write("यो संस्करणमा OpenRouter Jev AI को कडा JSON संरचना (Strict Schema Fix) मिलाइएको छ।")

# Sidebar - सेटिङहरू
asset_choice = st.sidebar.selectbox("क्रिप्टो एसेट छान्नुहोस्", ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"])
rr_ratio = st.sidebar.slider("रिस्क-रिवार्ड रेसियो (Risk:Reward)", 1.5, 4.0, 2.0, 0.5)
trail_pct = st.sidebar.slider("ट्रेलिङ स्टप प्रतिशत (Trailing Stop %)", 1.0, 5.0, 2.0, 0.5)

# Streamlit Secrets बाट API Key तान्ने
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    api_key = None

symbol_map = {"Bitcoin (BTC)": "BINANCE:BTCUSDT", "Ethereum (ETH)": "BINANCE:ETHUSDT", "Solana (SOL)": "BINANCE:SOLUSDT"}
tv_symbol = symbol_map[asset_choice]

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(f"📊 {asset_choice} लाइभ चार्ट")
    tv_widget = f"""
    <div class="tradingview-widget-container" style="width:100%; height:450px;">
      <iframe src="https://tradingview.com{tv_symbol}&interval=D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=light&style=1&timezone=Etc%2FUTC&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en" style="width: 100%; height: 100%; border: none;"></iframe>
    </div>
    """
    components.html(tv_widget, height=460)
    
    st.info("💡 माथिको चार्ट हेरेर हालको मूल्य र प्रवृत्ति तल भर्नुहोस्।")
    live_price_input = st.number_input("चार्टमा देखिएको हालको मूल्य (Live Price) हाल्नुहोस्:", min_value=0.0, value=84000.0)
    market_trend_input = st.selectbox("बजारको ट्रेन्ड (Trend)", ["Upward (उकालो)", "Downward (ओरालो)", "Sideways (तेर्सो)"])
    extra_notes = st.text_area("थप इन्डिकेटरहरू (वैकल्पिक)", value="RSI is healthy, price near support.")

with col2:
    st.subheader("🤖 Jev AI स्विंग निर्णय इन्जिन")
    
    if st.button("🎯 स्विंग ट्रेड प्लान डिजाइन गर्नुहोस्", use_container_width=True):
        if not api_key:
            st.error("🔒 त्रुटि: Streamlit Secrets मा OpenRouter API Key भेटिएन! कृपया Settings मा चेक गर्नुहोस्।")
        else:
            with St.spinner("Jev AI ले रणनीति गणना गर्दैछ..."):
                swing_state = (
                    f"Asset Symbol: {asset_choice}\n"
                    f"Current Live Price: \${live_price_input:,.2f}\n"
                    f"Market Trend: {market_trend_input}\n"
                    f"Technical Metrics: {extra_notes}\n"
                )
                
                # Jev AI को कडा JSON नियम (Schema Fix) अनुसार Payload
                jev_payload = {
                    "model": "typesafe/jev-1.13", 
                    "state": swing_state,
                    "questions": {
                        "decision": {
                            "type": "choice", 
                            "instructions": "Is this a high-quality swing trade setup?", 
                            "criteria": {
                                "SWING_BUY": "Good setup to buy and hold for a multi-day upward move.",
                                "SWING_SELL": "Good setup to short or sell for a multi-day downward move.",
                                "NO_TRADE": "The market is too choppy, unclear, or risky to enter right now."
                            }
                        },
                        "confidence": {
                            "type": "noul", 
                            "instructions": "Is the confidence of this signal high?"
                        },
                        "risk_mode": {
                            "type": "score", 
                            "instructions": "Rate current market risk for overnight position holding", 
                            "criteria": ["Conservative", "Moderate", "Aggressive", "Extreme"]
                        }
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                try:
                    response = requests.post("https://openrouter.ai", json=jev_payload, headers=headers)
                    
                    if response.status_code == 200:
                        res = response.json()
                        dec = res['questions']['decision']['value']
                        conf = f"{res['questions']['confidence']['probability']*100:.1f}%"
                        risk = res['questions']['risk_mode']['value_label']
                        
                        st.markdown(f"### Jev AI को निर्णय: **{dec}**")
                        st.write(f"**AI Metrics:** Confidence: `{conf}` | Risk Matrix: `{risk}`")
                        
                        if dec != "NO_TRADE":
                            sl_buffer = live_price_input * 0.02 
                            sl = live_price_input - sl_buffer if dec == "SWING_BUY" else live_price_input + sl_buffer
                            tp = live_price_input + (sl_buffer * rr_ratio) if dec == "SWING_BUY" else live_price_input - (sl_buffer * rr_ratio)
                            be = live_price_input + (sl_buffer * 0.5) if dec == "SWING_BUY" else live_price_input - (sl_buffer * 0.5)
                            
                            st.success(f"🎯 **स्टप लस (SL):** \${sl:,.2f}")
                            st.success(f"🎯 **टेक प्रोफिट (TP):** \${tp:,.2f}")
                            st.info(f"🛡️ **ब्रेक-इभन (Break-Even):** मूल्य \${be:,.2f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                            st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Stop सक्रिय भयो।")
                        else:
                            st.warning("⚠️ Jev AI ले अहिले बजार जोखिमपूर्ण भएकाले ट्रेड नलिन (NO_TRADE) सुझाव दिएको छ।")
                    else:
                        st.error(f"सर्भर प्रतिक्रिया त्रुटि ({response.status_code}): {response.text}")
                except Exception as e:
                    st.error(f"सञ्चार त्रुटि (Connection Error): {str(e)}")
