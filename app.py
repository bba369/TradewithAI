import streamlit as st
import requests

st.set_page_config(page_title="Jev AI Swing Planner", page_icon="📈", layout="centered")
st.title("📈 Jev AI Pro Swing Trading Planner")
st.write("बाइन्यान्सको लाइभ डाटा स्वतः तानी जेभ एआई (Jev AI) मार्फत स्विंग ट्रेड प्लान तयार गर्नुहोस्।")

api_key = st.sidebar.text_input("OpenRouter API Key", type="password")
asset_choice = st.sidebar.selectbox("क्रिप्टो एसेट छान्नुहोस्", ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"])
rr_ratio = st.sidebar.slider("रिस्क-रिवार्ड रेसियो (Risk:Reward)", 1.5, 4.0, 2.0, 0.5)
trail_pct = st.sidebar.slider("ट्रेलिङ स्टप प्रतिशत (Trailing Stop %)", 1.0, 5.0, 2.0, 0.5)

def fetch_swing_data(symbol):
    try:
        d_url = f"https://binance.com{symbol}&interval=1d&limit=14"
        h4_url = f"https://binance.com{symbol}&interval=4h&limit=20"
        d_res = requests.get(d_url).json()
        h4_res = requests.get(h4_url).json()
        live_price = float(h4_res[-1][4])
        h4_highs = [float(k[2]) for k in h4_res]
        h4_lows = [float(k[3]) for k in h4_res]
        avg_4h_range = sum([h - l for h, l in zip(h4_highs, h4_lows)]) / len(h4_res)
        
        swing_state = (
            f"Asset Symbol: {symbol}\nCurrent Live Price: ${live_price:,.2f}\n"
            f"Daily High/Low Range: ${min([float(k[3]) for k in d_res]):,.2f} to ${max([float(k[2]) for k in d_res]):,.2f}\n"
            f"Average 4H Candle Move: ${avg_4h_range:,.2f}\n"
        )
        return swing_state, live_price, avg_4h_range
    except: return None, 0, 0

if st.button("🎯 स्विंग ट्रेड प्लान डिजाइन गर्नुहोस्"):
    if not api_key:
        st.error("कृपया पहिले OpenRouter API Key हाल्नुहोस्!")
    else:
        symbol = {"Bitcoin (BTC)": "BTCUSDT", "Ethereum (ETH)": "ETHUSDT", "Solana (SOL)": "SOLUSDT"}[asset_choice]
        swing_state, live_price, avg_4h_range = fetch_swing_data(symbol)
        
        if live_price == 0:
            st.error("बाइन्यान्सबाट डाटा तान्न सकिएन।")
        else:
            jev_payload = {
                "model": "typesafe/jev-latest",
                "state": swing_state,
                "questions": {
                    "decision": {"type": "choice", "instructions": "Is this a high-quality swing trade setup?", "choices": ["SWING_BUY", "SWING_SELL", "NO_TRADE"]},
                    "confidence": {"type": "noul", "instructions": "High confidence?"},
                    "risk_mode": {"type": "score", "instructions": "Rate market risk", "criteria": ["Conservative", "Moderate", "Aggressive", "Extreme"]}
                }
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            res = requests.post("https://openrouter.ai", json=jev_payload, headers=headers).json()
            
            dec = res['questions']['decision']['value']
            conf = f"{res['questions']['confidence']['probability']*100:.1f}%"
            risk = res['questions']['risk_mode']['value_label']
            
            st.subheader(f"Jev AI निर्णय: {dec}")
            st.write(f"**AI Metrics:** Confidence: {conf} | Risk Matrix: {risk}")
            
            if dec != "NO_TRADE":
                sl_buffer = avg_4h_range * 1.5
                sl = live_price - sl_buffer if dec == "SWING_BUY" else live_price + sl_buffer
                tp = live_price + (sl_buffer * rr_ratio) if dec == "SWING_BUY" else live_price - (sl_buffer * rr_ratio)
                be = live_price + sl_buffer if dec == "SWING_BUY" else live_price - sl_buffer
                
                st.success(f"🎯 **स्टप लस (SL):** ${sl:,.2f}")
                st.success(f"🎯 **टेक प्रोफिट (TP):** ${tp:,.2f}")
                st.info(f"🛡️ **ब्रेक-इभन (Break-Even):** मूल्य ${be:,.2f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Active भयो।")
