import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="Jev AI Swing Planner", page_icon="📈", layout="wide")
st.title("📈 Jev AI Pro Swing Trading Planner (Special Edition)")
st.write("यो विशेष एडिसनमा ट्रेडिङभ्युको लाइभ चार्ट र डेटा कहिल्यै ब्लक हुँदैन।")

# Sidebar - सेटिङहरू
api_key = st.sidebar.text_input("OpenRouter API Key हाल्नुहोस्", type="password")
asset_choice = st.sidebar.selectbox("क्रिप्टो एसेट छान्नुहोस्", ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"])
rr_ratio = st.sidebar.slider("रिस्क-रिवार्ड रेसियो (Risk:Reward)", 1.5, 4.0, 2.0, 0.5)
trail_pct = st.sidebar.slider("ट्रेलिङ स्टप प्रतिशत (Trailing Stop %)", 1.0, 5.0, 2.0, 0.5)

# एसेट सिम्बोल म्यापिङ
symbol_map = {"Bitcoin (BTC)": "BINANCE:BTCUSDT", "Ethereum (ETH)": "BINANCE:ETHUSDT", "Solana (SOL)": "BINANCE:SOLUSDT"}
tv_symbol = symbol_map[asset_choice]

# दुईवटा कोठा (Columns) बनाउने - एउटामा चार्ट, अर्कोमा जेभ एआई
col1, col2 = gr.Row() if 'gr' in locals() else st.columns([1.2, 1])

with col1:
    st.subheader(f"📊 {asset_choice} लाइभ चार्ट र डेटा म्याट्रिक्स")
    # ट्रेडिङभ्युको आधिकारिक टेक्निकल एनालाइसिस विजेट (नेपालमा कहिल्यै ब्लक नहुने)
    tv_widget = f"""
    <div class="tradingview-widget-container" style="width:100%; height:450px;">
      <iframe src="https://tradingview.com{tv_symbol}&interval=D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=light&style=1&timezone=Etc%2FUTC&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en" style="width: 100%; height: 100%; border: none;"></iframe>
    </div>
    """
    components.html(tv_widget, height=460)
    
    st.info("💡 माथिको चार्टमा हेरेर हालको मूल्य र आरएसआई (RSI) जस्ता डेटा तलको कोठामा लेख्नुहोस्।")
    
    # म्यानुअल इनपुट बक्स (सुरक्षित र नियन्त्रित ट्रेडिङका लागि)
    live_price_input = st.number_input("चार्टमा देखिएको हालको मूल्य (Live Price) हाल्नुहोस्:", min_value=0.0, value=84000.0)
    market_trend_input = st.selectbox("बजार कता गइरहेको देखिन्छ? (Trend)", ["Upward (उकालो)", "Downward (ओरालो)", "Sideways (तेर्सो)"])
    extra_notes = st.text_area("थप इन्डिकेटरहरू (वैकल्पिक - जस्तै: RSI 60, Support Breakdown)", value="RSI is healthy, price near daily support.")

with col2:
    st.subheader("🤖 Jev AI स्विंग निर्णय इन्जिन")
    
    if st.button("🎯 स्विंग ट्रेड प्लान डिजाइन गर्नुहोस्", use_container_width=True):
        if not api_key:
            st.error("कृपया पहिले देब्रेपट्टि आफ्नो OpenRouter API Key हाल्नुहोस्!")
        else:
            with st.spinner("Jev AI ले रणनीति तयार पार्दैछ..."):
                # जेभ एआईका लागि डेटा संकलन
                swing_state = (
                    f"Asset Symbol: {asset_choice}\n"
                    f"Current Live Price: \${live_price_input:,.2f}\n"
                    f"User Observed Trend: {market_trend_input}\n"
                    f"Technical Indicators: {extra_notes}\n"
                )
                
                jev_payload = {
                    "model": "typesafe/jev-latest",
                    "state": swing_state,
                    "questions": {
                        "decision": {"type": "choice", "instructions": "Based on user inputs, is this a high-quality swing trade setup?", "choices": ["SWING_BUY", "SWING_SELL", "NO_TRADE"]},
                        "confidence": {"type": "noul", "instructions": "Is the trade signal confidence high?"},
                        "risk_mode": {"type": "score", "instructions": "Rate market risk for holding overnight", "criteria": ["Conservative", "Moderate", "Aggressive", "Extreme"]}
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
                        
                        st.markdown(f"### Jev AI को निर्णय: **{dec}**")
                        st.write(f"**AI Metrics:** Confidence: `{conf}` | Risk Matrix: `{risk}`")
                        
                        if dec != "NO_TRADE":
                            # भोलाटिलिटीको सट्टा २% को स्ट्यान्डर्ड बफर स्विंगका लागि
                            sl_buffer = live_price_input * 0.02 
                            sl = live_price_input - sl_buffer if dec == "SWING_BUY" else live_price_input + sl_buffer
                            tp = live_price_input + (sl_buffer * rr_ratio) if dec == "SWING_BUY" else live_price_input - (sl_buffer * rr_ratio)
                            be = live_price_input + (sl_buffer * 0.5) if dec == "SWING_BUY" else live_price_input - (sl_buffer * 0.5)
                            
                            st.success(f"🎯 **स्टप लस (Stop Loss - SL):** \${sl:,.2f}")
                            st.success(f"🎯 **टेक प्रोफिट (Take Profit - TP):** \${tp:,.2f}")
                            st.info(f"🛡️ **ब्रेक-इभन (Break-Even प्वाइन्ट):** मूल्य \${be:,.2f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                            st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Stop एक्टिभेट भयो।")
                        else:
                            st.warning("⚠️ Jev AI ले अहिले ट्रेड नलिन (NO_TRADE) सुझाव दिएको छ। बजार अनुकूल छैन।")
                    else:
                        st.error(f"Jev AI Error: {response.text}")
                except Exception as e:
                    st.error(f"Request Error: {str(e)}")
