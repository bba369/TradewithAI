import streamlit as st
import requests

st.set_page_config(page_title="Jev AI Swing Planner", page_icon="📈", layout="centered")
st.title("📈 Jev AI Pro Swing Trading Planner")
st.write("बजारको लाइभ डेटा स्वतः तानी जेभ एआई (Jev AI) मार्फत स्विंग ट्रेड प्लान तयार गर्नुहोस्।")

api_key = st.sidebar.text_input("OpenRouter API Key", type="password")
asset_choice = st.sidebar.selectbox("क्रिप्टो एसेट छान्नुहोस्", ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"])
rr_ratio = st.sidebar.slider("रिस्क-रिवार्ड रेसियो (Risk:Reward)", 1.5, 4.0, 2.0, 0.5)
trail_pct = st.sidebar.slider("ट्रेलिङ स्टप प्रतिशत (Trailing Stop %)", 1.0, 5.0, 2.0, 0.5)

def fetch_swing_data(symbol):
    # विकल्प १: नेपालका लागि बाइन्यान्सको वैकल्पिक सार्वजनिक सर्भर (Alternative API API)
    try:
        d_url = f"https://binance.com{symbol}&interval=1d&limit=14"
        h4_url = f"https://binance.com{symbol}&interval=4h&limit=20"
        d_res = requests.get(d_url, timeout=5).json()
        h4_res = requests.get(h4_url, timeout=5).json()
        
        live_price = float(h4_res[-1])
        h4_highs = [float(k) for k in h4_res]
        h4_lows = [float(k) for k in h4_res]
        avg_4h_range = sum([h - l for h, l in zip(h4_highs, h4_lows)]) / len(h4_res)
        
        swing_state = (
            f"Asset Symbol: {symbol}\nCurrent Live Price: ${live_price:,.2f}\n"
            f"Daily High/Low Range: ${min([float(k) for k in d_res]):,.2f} to ${max([float(k) for k in d_res]):,.2f}\n"
            f"Average 4H Candle Move: ${avg_4h_range:,.2f}\n"
        )
        return swing_state, live_price, avg_4h_range
    except:
        pass

    # विकल्प २: यदि बाइन्यान्स चल्दै चलेन भने Yahoo Finance बाट ब्याकअप डाटा तान्ने
    try:
        ticker = "BTC-USD" if "BTC" in symbol else "ETH-USD" if "ETH" in symbol else "SOL-USD"
        url = f"https://yahoo.com{ticker}?interval=1d&range=1mo"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5).json()
        result = res['chart']['result']
        live_price = result['meta']['regularMarketPrice']
        high_prices = result['indicators']['quote']['high']
        low_prices = result['indicators']['quote']['low']
        avg_4h_range = (max(high_prices[-5:]) - min(low_prices[-5:])) / 5
        
        swing_state = (
            f"Asset Symbol: {symbol}\nCurrent Live Price: ${live_price:,.2f}\n"
            f"Recent High/Low Range: ${min(low_prices[-14:]):,.2f} to ${max(high_prices[-14:]):,.2f}\n"
            f"Estimated Volatility Buffer: ${avg_4h_range:,.2f}\n"
        )
        return swing_state, live_price, avg_4h_range
    except:
        return None, 0, 0

if st.button("🎯 स्विंग ट्रेड प्लान डिजाइन गर्नुहोस्"):
    if not api_key:
        st.error("कृपया पहिले OpenRouter API Key हाल्नुहोस्!")
    else:
        symbol = {"Bitcoin (BTC)": "BTCUSDT", "Ethereum (ETH)": "ETHUSDT", "Solana (SOL)": "SOLUSDT"}[asset_choice]
        swing_state, live_price, avg_4h_range = fetch_swing_data(symbol)
        
        if live_price == 0:
            st.error("बजारबाट डाटा तान्न सकिएन। कृपया केही समयपछि प्रयास गर्नुहोस्।")
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
            
            try:
                response = requests.post("https://openrouter.ai", json=jev_payload, headers=headers)
                if response.status_code == 200:
                    res = response.json()
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
                else:
                    st.error(f"Jev AI Error: {response.text}")
            except Exception as e:
                st.error(f"Request Error: {str(e)}")
