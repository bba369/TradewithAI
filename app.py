import streamlit as st
import requests

st.set_page_config(page_title="Jev AI Pro Swing Planner", page_icon="📈", layout="wide")

st.title("📈 Jev AI Pro Swing Trading Planner (Standard API Edition)")
st.write("यो संस्करणमा OpenRouter Jev AI को लागि आवश्यक अनिवार्य सेक्युरिटी हेडर्स (Strict Headers Fix) मिलाइएको छ।")

# Sidebar - जोखिम र रणनीति सेटिङहरू
st.sidebar.header("🛡️ जोखिम र रणनीति सेटिङ")
rr_ratio = st.sidebar.slider("रिस्क-रिवार्ड रेसियो (Risk:Reward)", 1.5, 4.0, 2.0, 0.5)
trail_pct = st.sidebar.slider("ट्रेलिङ स्टप प्रतिशत (Trailing Stop %)", 1.0, 5.0, 2.0, 0.5)

# Streamlit Secrets बाट API Key तान्ने
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    api_key = None

col1, col2 = st.columns(2, gap="large")

# ==================== FRAME 1: INSTRUCTIONS ====================
with col1:
    st.markdown("### 🔍 चरण १: चार्ट डेटा संकलन (Easy Method)")
    st.info(
        "💡 **कसरी गर्ने?**\n"
        "१. आफ्नो HTF (4H) र LTF (15M) चार्टको स्क्रिनसट लिनुहोस्।\n"
        "२. उक्त फोटोलाई **ChatGPT** वा **Google Lens** मा हालेर विवरण निकालनाहोस्।\n"
        "३. त्यहाँबाट प्राप्त भएको विवरण (Text) लाई कपी गरेर दायाँपट्टिको बाकसमा पेस्ट गर्नुहोस्।"
    )
    
    st.markdown("#### 📝 थप सहयोगी नोटहरू (Optional)")
    extra_notes = st.text_area("थप कुरा (जस्तै: RSI 60, Breakout आदि):", value="RSI is healthy, price near daily support.")

# ==================== FRAME 2: JEV AI ENGINE ====================
with col2:
    st.markdown("### 🤖 चरण २: जेभ एआई स्विंग निर्णय इन्जिन (Jev AI)")
    st.write("बजारको विवरण यहाँ पेस्ट गर्नुहोस् र हालको मूल्य अंकमा हाल्नुहोस्।")
    
    paste_data = st.text_area("📥 बजारको विवरण यहाँ पेस्ट गर्नुहोस् (Paste Market Text Data Here):", height=180, 
                              placeholder="Asset: SOLUSDT\nPrice: \$116.41\nHTF Trend: Bullish...")
    
    live_price_num = st.number_input("हालको मूल्य अंकमा हाल्नुहोस् (Calculations को लागि):", min_value=0.0, value=116.41, step=0.01)
    
    if st.button("🎯 स्विंग ट्रेड प्लान डिजाइन गर्नुहोस्", use_container_width=True):
        if not api_key:
            st.error("🔒 Secrets मा OpenRouter API Key भेटिएन! कृपया पहिले थप्नुहोस्।")
        elif not paste_data:
            st.warning("⚠️ कृपया पहिले बजारको डेटा (Text) यहाँ पेस्ट गर्नुहोस्।")
        else:
            with st.spinner("Jev AI ले रणनीति तयार पार्दैछ..."):
                combined_state = paste_data + f"\nAdditional Context: {extra_notes}"
                
                # Jev AI (Strict Response Formatting) Payload
                jev_payload = {
                    "model": "typesafe/jev-1.13", 
                    "state": combined_state,
                    "questions": {
                        "decision": {
                            "type": "choice", 
                            "instructions": "What is the best swing action?", 
                            "criteria": {
                                "SWING_BUY": "Good setup to buy and hold.",
                                "SWING_SELL": "Good setup to short or sell.",
                                "NO_TRADE": "Market is too choppy or risky."
                            }
                        },
                        "confidence": {
                            "type": "noul", 
                            "instructions": "Is confidence high?"
                        },
                        "risk_mode": {
                            "type": "score", 
                            "instructions": "Rate market risk", 
                            "criteria": ["Conservative", "Moderate", "Aggressive", "Extreme"]
                        }
                    }
                }
                
                # --- मुख्य फिक्स: OpenRouter ले अनिवार्य रूपमा माग्ने सेक्युरिटी हेडर्स ---
                headers = {
                    "Authorization": f"Bearer {api_key}", 
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://streamlit.io",  # अनिवार्य हेडर १
                    "X-Title": "Jev AI Trading Bot"         # अनिवार्य हेडर २
                }
                
                try:
                    res_raw = requests.post("https://openrouter.ai", json=jev_payload, headers=headers)
                    
                    if res_raw.status_code != 200:
                        st.error(f"❌ OpenRouter API Error ({res_raw.status_code}): {res_raw.text}")
                        st.stop()
                        
                    try:
                        res = res_raw.json()
                    except Exception:
                        st.warning("⚠️ सर्भरले JSON को सट्टा टेक्स्ट रेस्पोन्स पठायो। वास्तविक म्यासेज तल हेर्नुहोस्:")
                        st.code(res_raw.text)
                        st.stop()
                    
                    if "error" in res:
                        st.error(f"❌ सर्भर त्रुटि: {res['error'].get('message', res['error'])}")
                        st.stop()
                        
                    # लचिलो रेस्पोन्स पार्सिङ
                    answers = res.get('answers', res.get('questions', res))
                    
                    dec_obj = answers.get('decision', {})
                    dec = dec_obj.get('choice', dec_obj.get('value', 'NO_TRADE'))
                    
                    conf_obj = answers.get('confidence', {})
                    conf_prob = conf_obj.get('probability', 0.5)
                    
                    risk_obj = answers.get('risk_mode', {})
                    risk = risk_obj.get('value_label', risk_obj.get('value', 'Moderate'))
                    
                    st.markdown(f"### Jev AI को निर्णय: **{dec}**")
                    st.write(f"**AI Metrics:** Confidence: `{conf_prob * 100:.1f}%` | Risk Matrix: `{risk}`")
                    st.markdown("---")
                    st.markdown("### 💡 Jev AI अतिरिक्त व्यापारिक सुझाव (Trading Suggestions):")
                    
                    if dec == "NO_TRADE":
                        st.warning("⚠️ Jev AI ले अहिले बजार सुरक्षित नभएकाले ट्रेड नलिन (NO_TRADE) सुझाव दिएको छ।")
                        st.info(
                            "📌 **Pro Suggestions for NO_TRADE:**\n"
                            f"- **पर्ख र हेर (Wait & Watch):** Jev को विश्वास केवल {conf_prob * 100:.1f}% मात्र छ। बजार चौपी (Choppy) भएकाले पूंजी सुरक्षित राख्नुहोस्।"
                        )
                    else:
                        sl_buffer = live_price_num * 0.02 
                        sl = live_price_num - sl_buffer if dec == "SWING_BUY" else live_price_num + sl_buffer
                        tp = live_price_num + (sl_buffer * rr_ratio) if dec == "SWING_BUY" else live_price_num - (sl_buffer * rr_ratio)
                        be = live_price_num + (sl_buffer * 0.5) if dec == "SWING_BUY" else live_price_num - (sl_buffer * 0.5)
                        
                        st.success(f"🎯 **स्टप लस (SL):** \${sl:,.3f}")
                        st.success(f"🎯 **टेक प्रोफिट (TP):** \${tp:,.3f}")
                        st.info(f"🛡️ **ब्रेक-इभन (Break-Even):** मूल्य \${be:,.3f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                        st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Stop सक्रिय भयो।")
                        
                except Exception as e:
                    st.error(f"प्रक्रिया त्रुटि: {str(e)}")
