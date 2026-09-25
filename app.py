import streamlit as st
import requests

st.set_page_config(page_title="Jev AI Pro Swing Planner", page_icon="📈", layout="wide")

st.title("📈 Jev AI Pro Swing Trading Planner (Ultimate Fix)")
st.write("यो एडिसनमा सर्भरको जुनसुकै प्रतिक्रिया (HTML/JSON) लाई सुरक्षित रूपमा ह्यान्डल गरिएको छ।")

# Sidebar - जोखिम र रणनीति सेटिङहरू
st.sidebar.header("🛡️ जोखिम र रणनीति सेटिङ")
rr_ratio = st.sidebar.slider("रिस्क-रिवार्ड रेसियो (Risk:Reward)", 1.5, 4.0, 2.0, 0.5)
trail_pct = st.sidebar.slider("ट्रेलिङ स्टप प्रतिशत (Trailing Stop %)", 1.0, 5.0, 2.0, 0.5)

# Streamlit Secrets बाट API Key तान्ने
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    api_key = None

# दुईवटा स्पष्ट फ्रेम (Columns)
col1, col2 = st.columns(2, gap="large")

# ==================== FRAME 1: INSTRUCTIONS (देब्रेपट्टि) ====================
with col1:
    st.markdown("### 🔍 चरण १: चार्ट डेटा संकलन (Easy Method)")
    st.info(
        "💡 **कसरी गर्ने?**\n"
        "१. आफ्नो HTF (4H) र LTF (15M) चार्टको स्क्रिनसट लिनुहोस्।\n"
        "२. उक्त फोटोलाई **ChatGPT** वा **Google Lens** मा हालेर विवरण निकाल्नुहोस्।\n"
        "३. त्यहाँबाट प्राप्त भएको विवरण (Text) लाई कपी गरेर दायाँपट्टिको बाकसमा पेस्ट गर्नुहोस्।"
    )
    
    st.markdown("#### 📝 थप सहयोगी नोटहरू (Optional)")
    extra_notes = st.text_area("थप कुरा (जस्तै: RSI 60, Breakout आदि):", value="RSI is healthy, price near daily support.")

# ==================== FRAME 2: JEV AI ENGINE (दायाँपट्टि) ====================
with col2:
    st.markdown("### 🤖 चरण २: जेभ एआई स्विंग निर्णय इन्जिन (Jev AI)")
    st.write("बजारको विवरण यहाँ पेस्ट गर्नुहोस् र हालको मूल्य अंकमा हाल्नुहोस्।")
    
    paste_data = st.text_area("📥 बजारको विवरण यहाँ पेस्ट गर्नुहोस् (Paste Market Text Data Here):", height=180, 
                              placeholder="Asset: BTC/USDT\nPrice: \$84000...")
    
    live_price_num = st.number_input("हालको मूल्य अंकमा हाल्नुहोस् (Calculations को लागि):", min_value=0.0, value=84248.0, step=1.0)
    
    if st.button("🎯 स्विंग ट्रेड प्लान डिजाइन गर्नुहोस्", use_container_width=True):
        if not api_key:
            st.error("🔒 Secrets मा OpenRouter API Key भेटिएन! कृपया पहिले Settings मा थप्नुहोस्।")
        elif not paste_data:
            st.warning("⚠️ कृपया पहिले बजारको डेटा (Text) यहाँ पेस्ट गर्नुहोस्।")
        else:
            with st.spinner("Jev AI ले रणनीति तयार पार्दैछ..."):
                combined_state = paste_data + f"\nAdditional Context: {extra_notes}"
                
                jev_payload = {
                    "model": "typesafe/jev-1.13", 
                    "state": combined_state,
                    "questions": {
                        "decision": {
                            "type": "choice", 
                            "instructions": "Based on the market state text, what is the best swing action?", 
                            "criteria": {
                                "SWING_BUY": "Good setup to buy and hold.",
                                "SWING_SELL": "Good setup to short or sell.",
                                "NO_TRADE": "Market is too choppy or risky."
                            }
                        },
                        "confidence": {
                            "type": "noul", 
                            "instructions": "Is the confidence high?"
                        },
                        "risk_mode": {
                            "type": "score", 
                            "instructions": "Rate market risk", 
                            "criteria": ["Conservative", "Moderate", "Aggressive", "Extreme"]
                        }
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {api_key}", 
                    "Content-Type": "application/json"
                }
                
                try:
                    res_raw = requests.post("https://openrouter.ai/api/alpha/decisions", json=jev_payload, headers=headers)
                    
                    # --- मुख्य फिक्स: पहिले रेस्पोन्स टेक्स्ट हो कि JSON हो जाँच्ने (Ultimate Format Safeguard) ---
                    try:
                        res = res_raw.json()
                    except Exception:
                        # यदि सर्भरले HTML एरर पठायो भने सिधै म्यासेज देखाउने
                        st.error(f"❌ OpenRouter सर्भर एरर ({res_raw.status_code}): खातामा ब्यालेन्स/क्रेडिट नभएको वा API Key बिग्रिएको हुन सक्छ।")
                        st.warning("💡 कृपया openrouter.ai/dashboard मा गई ब्यालेन्स चेक गर्नुहोस्। न्यू एकाउन्टमा \$0 ब्यालेन्स हुँदा जेभ एआई चल्दैन।")
                        st.stop()
                    
                    if res_raw.status_code == 200:
                        # लचिलो रेस्पोन्स म्यापिङ (Flexible Parsing)
                        answers = res.get('answers', res.get('questions', res))
                        
                        dec_obj = answers.get('decision', {})
                        dec = dec_obj.get('choice', dec_obj.get('value', 'NO_TRADE'))
                        
                        conf_obj = answers.get('confidence', {})
                        conf_prob = conf_obj.get('probability', 0.5)
                        
                        risk_obj = answers.get('risk_mode', {})
                        risk = risk_obj.get('value_label', risk_obj.get('value', 'Moderate'))
                        
                        st.markdown(f"### Jev AI को निर्णय: **{dec}**")
                        st.write(f"**AI Metrics:** Confidence: `{conf_prob * 100:.1f}%` | Risk Matrix: `{risk}`")
                        
                        if dec in ["SWING_BUY", "SWING_SELL"]:
                            sl_buffer = live_price_num * 0.02 
                            sl = live_price_num - sl_buffer if dec == "SWING_BUY" else live_price_num + sl_buffer
                            tp = live_price_num + (sl_buffer * rr_ratio) if dec == "SWING_BUY" else live_price_num - (sl_buffer * rr_ratio)
                            be = live_price_num + (sl_buffer * 0.5) if dec == "SWING_BUY" else live_price_num - (sl_buffer * 0.5)
                            
                            st.success(f"🎯 **स्टप लस (SL):** \${sl:,.2f}")
                            st.success(f"🎯 **टेक प्रोफिट (TP):** \${tp:,.2f}")
                            st.info(f"🛡️ **ब्रेक-इभन (Break-Even):** मूल्य \${be:,.2f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                            st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Stop सक्रिय भयो।")
                        else:
                            st.warning("⚠️ Jev AI ले अहिले बजार सुरक्षित नभएकाले ट्रेड नलिन (NO_TRADE) सुझाव दिएको छ।")
                    else:
                        st.error(f"Jev AI API Error ({res_raw.status_code}): {res}")
                except Exception as e:
                    st.error(f"प्रक्रिया त्रुटि: {str(e)}")
