import streamlit as st
import requests

st.set_page_config(page_title="Jev AI Pro Swing Planner", page_icon="📈", layout="wide")

st.title("📈 Jev AI Pro Swing Trading Planner (With Pro Suggestions)")
st.write("यो एडिसनमा Jev AI को निर्णय अनुसार ट्रेडरका लागि विशेष व्यावहारिक सुझावहरू (Trading Suggestions) थप गरिएको छ।")

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
    
    live_price_num = st.number_input("हालको मूल्य अंकमा हाल्नुहोस् (Calculations को लागि):", min_value=0.0, value=116.41, step=0.01)
    
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
                    res_raw = requests.post("https://openrouter.ai", json=jev_payload, headers=headers)
                    
                    try:
                        res = res_raw.json()
                    except Exception:
                        st.error(f"❌ OpenRouter सर्भर एरर ({res_raw.status_code}): खातामा ब्यालेन्स/क्रेडिट नभएको वा API Key बिग्रिएको हुन सक्छ।")
                        st.stop()
                    
                    if res_raw.status_code == 200:
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
                            st.warning("⚠️ **Jev AI ले अहिले बजार सुरक्षित नभएकाले ट्रेड नलिन (NO_TRADE) सुझाव दिएको छ।**")
                            st.info(
                                "📌 **Pro Suggestions for NO_TRADE:**\n"
                                f"- **पर्ख र हेर (Wait & Watch):** Jev को विश्वास केवल {conf_prob * 100:.1f}% मात्र छ। बजारमा अहिले 'Volume Compression' र 'Sideways Choppiness' भएकाले कुनै पनि दिशा निश्चित छैन। जबरजस्ती ट्रेड नलिनुहोस्।\n"
                                "- **सपोर्ट/रेजिस्टेन्स ब्रेकआउट पर्खिनुहोस्:** मूल्यलाई अघिल्लो स्विंग हाई (SOL को लागि \$११८-१२०) भन्दा माथि वा बलियो सपोर्ट (११४) भन्दा तल स्पष्ट रूपमा निस्कन दिनुहोस्।\n"
                                "- **पूंजी सुरक्षित राख्नुहोस्:** बजार चौपी (Choppy) भएको बेला ट्रेडिङ शुल्क र साना स्टप-लस बारम्बार हिट भएर पैसा नाश हुन सक्छ। उत्तम सेटअप नआएसम्म ढुक्कसँग बस्नुहोस्।"
                            )
                        
                        elif dec == "SWING_BUY":
                            sl_buffer = live_price_num * 0.02 
                            sl = live_price_num - sl_buffer
                            tp = live_price_num + (sl_buffer * rr_ratio)
                            be = live_price_num + (sl_buffer * 0.5)
                            
                            st.success(f"🎯 **स्टप लस (SL):** \${sl:,.3f}")
                            st.success(f"🎯 **टेक प्रोफिट (TP):** \${tp:,.3f}")
                            st.info(f"🛡️ **ब्रेक-इभन (Break-Even):** मूल्य \${be:,.3f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                            st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Stop सक्रिय भयो।")
                            
                            st.info(
                                "📌 **Pro Suggestions for SWING_BUY:**\n"
                                "- **इन्ट्री नियम:** मूल्य वर्तमान स्तरमा स्थिर रहेमा मात्र थोरै परिमाण (Risk Capital को १-२%) बाट खरिद सुरु गर्नुहोस्।\n"
                                "- **कन्फर्मेसन:** यदि मूल्य ब्रेक-इभन विन्दु भन्दा माथि जान्छ भने मात्र थप पोजिसन (Scale-In) थप्नुहोस्।"
                            )
                            
                        elif dec == "SWING_SELL":
                            sl_buffer = live_price_num * 0.02 
                            sl = live_price_num + sl_buffer
                            tp = live_price_num - (sl_buffer * rr_ratio)
                            be = live_price_num - (sl_buffer * 0.5)
                            
                            st.success(f"🎯 **स्टप लस (SL):** \${sl:,.3f}")
                            st.success(f"🎯 **टेक प्रोफिट (TP):** \${tp:,.3f}")
                            st.info(f"🛡️ **ब्रेक-इभन (Break-Even):** मूल्य \${be:,.3f} पुगेपछि SL लाई इन्ट्री मूल्यमा सार्नुहोस्।")
                            st.warning(f"🔄 **ट्रेलिङ स्टप:** {trail_pct}% Trailing Stop सक्रिय भयो।")
                            
                            st.info(
                                "📌 **Pro Suggestions for SWING_SELL:**\n"
                                "- **सर्ट सेलिङ नियम:** १५ मिनेटको चार्टमा बेरिस मोमेन्टम (Bearish Crossover) पुष्टी भइरहेकाले यो योजना बनेको हो।\n"
                                "- **सतर्कता:** ओभरनाइट (Overnight) पोजिसन होल्ड गर्दा बजारमा अचानक आउने शर्ट-स्क्विज (Short Squeeze) बाट बच्न SL कडा रूपमा लागू गर्नुहोस्।"
                            )
                    else:
                        st.error(f"Jev AI API Error ({res_raw.status_code}): {res}")
                except Exception as e:
                    st.error(f"प्रक्रिया त्रुटि: {str(e)}")
