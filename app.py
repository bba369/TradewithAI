import streamlit as st
import requests
import base64

st.set_page_config(page_title="Dual-Step Jev AI Swing Planner", page_icon="📈", layout="wide")

st.title("📈 Dual-Step Jev AI Pro Swing Trading Planner")
st.write("यो एपले दुईवटा चरणमा काम गर्छ: पहिले चार्टको फोटोबाट डेटा निकाल्छ, र त्यसपछि Jev AI मार्फत स्विंग प्लान बनाउँछ।")

# Sidebar सेटिङहरू
st.sidebar.header("🛡️ जोखिम र रणनीति सेटिङ")
rr_ratio = st.sidebar.slider("रिस्क-रिवार्ड रेसियो (Risk:Reward)", 1.5, 4.0, 2.0, 0.5)
trail_pct = st.sidebar.slider("ट्रेलिङ स्टप प्रतिशत (Trailing Stop %)", 1.0, 5.0, 2.0, 0.5)

# Streamlit Secrets बाट API Key तान्ने
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    api_key = None

# दुईवटा छुट्टाछुट्टै फ्रेम (Columns) बनाउने
col1, col2 = st.columns([1, 1], gap="large")

# ==================== STEP 1 FRAME (देब्रेपट्टि) ====================
with col1:
    st.markdown("### 🔍 चरण १: चार्ट अपलोड र डेटा एक्सट्र्याक्सन (Vision AI)")
    st.write("हायर टाइमफ्रेम (HTF) र लोअर टाइमफ्रेम (LTF) को स्क्रिनसट हाल्नुहोस्।")
    
    htf_file = st.file_uploader("१. हायर टाइमफ्रेम फोटो हाल्नुहोस् (HTF - जस्तै: 4H/1D चार्ट)", type=["jpg", "jpeg", "png"])
    ltf_file = st.file_uploader("२. लोअर टाइमफ्रेम फोटो हाल्नुहोस् (LTF - जस्तै: 5M/15M चार्ट)", type=["jpg", "jpeg", "png"])
    extra_context = st.text_input("थप नोट (वैकल्पिक - जस्तै: बजारको कुनै समाचार)", placeholder="e.g., FOMC news in 1 hour")
    
    if st.button("🤖 फोटोबाट डेटा निकाल्नुहोस्", use_container_width=True):
        if not api_key:
            st.error("🔒 Secrets मा OpenRouter API Key भेटिएन!")
        elif not htf_file or not ltf_file:
            st.warning("⚠️ कृपया HTF र LTF दुवै चार्टको फोटो अपलोड गर्नुहोस्।")
        else:
            with st.spinner("Vision AI ले चार्टका फोटोहरू पढ्दैछ..."):
                # फोटोहरूलाई Base64 मा बदल्ने
                htf_base64 = base64.b64encode(htf_file.read()).decode('utf-8')
                ltf_base64 = base64.b64encode(ltf_file.read()).decode('utf-8')
                
                vision_prompt = f"""
                You are a professional trading chart analyst. Analyze these two images:
                Image 1: Higher Timeframe (HTF) chart for broad trend.
                Image 2: Lower Timeframe (LTF) chart for immediate entry.
                Extra User Context: {extra_context}
                
                Extract and list the following parameters in a clean summary format:
                - Asset Name/Symbol:
                - Approximate Current Price:
                - HTF Trend (Upward/Downward/Sideways):
                - LTF Trend & Immediate Price Action:
                - Key Technical Indicator status visible (e.g., RSI, MACD, or Moving Averages):
                Keep it concise and structured.
                """
                
                payload = {
                    "model": "google/gemini-2.5-flash",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": vision_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{htf_base64}"}},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{ltf_base64}"}}
                            ]
                        }
                    ]
                }
                
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                
                try:
                    response = requests.post("https://openrouter.ai", json=payload, headers=headers)
                    if response.status_code == 200:
                        raw_data = response.json()['choices']['message']['content']
                        st.success("✅ फोटोबाट डेटा सफलतापूर्वक निकालियो!")
                        st.text_area("📋 यो डेटा कपी गर्नुहोस् (Copy this output):", value=raw_data, height=250)
                    else:
                        st.error(f"Vision Error ({response.status_code}): {response.text}")
                except Exception as e:
                    st.error(f"सञ्चार त्रुटि: {str(e)}")

# ==================== STEP 2 FRAME (दायाँपट्टि) ====================
with col2:
    st.markdown("### 🤖 चरण २: जेभ एआई स्विंग निर्णय इन्जिन (Jev AI)")
    st.write("चरण १ बाट कपी गरेको डेटा यहाँ पेस्ट गर्नुहोस् र हालको मूल्य नम्बरमा हाल्नुहोस्।")
    
    # प्रयोगकर्ताले कपी-पेस्ट गर्ने ठाउँ
    paste_data = st.text_area("📥 चरण १ को आउटपुट यहाँ पेस्ट गर्नुहोस् (Paste Data Here):", height=150, placeholder="Asset Name: BTC/USDT\nPrice: \$84000...")
    live_price_num = st.number_input("चार्टमा देखिएको हालको मूल्य अंकमा हाल्नुहोस् (Calculations को लागि):", min_value=0.0, value=84000.0, step=1.0)
    
    if st.button("🎯 स्विंग ट्रेड प्लान डिजाइन गर्नुहोस्", use_container_width=True):
        if not api_key:
            st.error("🔒 Secrets मा OpenRouter API Key भेटिएन!")
        elif not paste_data:
            st.warning("⚠️ कृपया पहिले चरण १ को डेटा यहाँ पेस्ट गर्नुहोस्।")
        else:
            with st.spinner("Jev AI ले स्विंग रणनीति तयार पार्दैछ..."):
                jev_payload = {
                    "model": "typesafe/jev-1.13", 
                    "state": paste_data,
                    "questions": {
                        "decision": {
                            "type": "choice", 
                            "instructions": "Based on the provided market state text, is this a high-quality swing trade setup?", 
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
                
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                
                try:
                    res_raw = requests.post("https://openrouter.ai", json=jev_payload, headers=headers)
                    if res_raw.status_code == 200:
                        res = res_raw.json()
                        answers = res.get('answers', {})
                        
                        dec = answers['decision']['choice']
                        conf_prob = answers['confidence']['probability']
                        risk = answers['risk_mode']['value_label']
                        
                        st.markdown(f"### Jev AI को निर्णय: **{dec}**")
                        st.write(f"**AI Metrics:** Confidence: `{conf_prob * 100:.1f}%` | Risk Matrix: `{risk}`")
                        
                        if dec != "NO_TRADE":
                            # २% को भोलाटिलिटी बफर स्विंगका लागि
                            sl_buffer = live_price_num * 0.02 
                            sl = live_price_num - sl_buffer if dec == "SWING_BUY" else live_price_num + sl_buffer
                            tp = live_price_num + (sl_buffer * rr_ratio) if dec == "SWING_BUY" else live_price_num - (sl_buffer * rr_ratio)
                            be = live_price_num + (sl_buffer * 0.5) if dec == "SWING_BUY" else live_price_input + (sl_buffer * 0.5) if 'live_price_input' in locals() else live_price_num + (sl_buffer * 0.5) if dec == "SWING_BUY" else live_price_num - (sl_buffer * 0.5)
                            
                            st.success(f"🎯 **स्टप लस (SL):** \${sl:,.2f}")
                            st.success(f"🎯 **टेक प्रोफिट (TP):** \${tp:,.2f}")
                            st.info(f"🛡️ **ब्रेक-इभन (Break-Even):** मूल्य \${be:,.2f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                            st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Stop सक्रिय भयो।")
                        else:
                            st.warning("⚠️ Jev AI ले अहिले बजार सुरक्षित नभएकाले ट्रेड नलिन (NO_TRADE) सुझाव दिएको छ।")
                    else:
                        st.error(f"Jev AI API Error ({res_raw.status_code}): {res_raw.text}")
                except Exception as e:
                    st.error(f"सञ्चार त्रुटि: {str(e)}")
