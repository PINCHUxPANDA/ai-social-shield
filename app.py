import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.scraper import fetch_instagram_data
from src.predict import hybrid_shield_detector
from src.database import init_db, log_scan, get_all_logs

init_db()

st.set_page_config(page_title="AI Social Shield Pro", page_icon="🛡️", layout="wide")

st.title("🛡️ AI Social Shield: Multi-Modal Dashboard")
st.markdown("Automated identification of spam profiles using Hybrid Machine Learning & NLP models.")
st.write("---")

target_user = st.text_input("Enter Instagram Username (e.g., @cristiano or any public handle)", "")

if st.button("Run Full Cyber-Scan", use_container_width=True):
    if target_user:
        username = target_user.replace("@", "").strip()
        
        with st.spinner("Fetching live metrics & evaluating threat vectors..."):
            data = fetch_instagram_data(username)
            
            if data:
                final_score, p_acc, p_comm, p_img, explanation = hybrid_shield_detector(data)
                
                log_scan(username, round(final_score * 100, 2))
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("⚡ Threat Meter")
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = final_score * 100,
                        title = {'text': "Overall Threat Index (%)", 'font': {'size': 20}},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkred" if final_score > 0.5 else "darkgreen"},
                            'steps': [
                                {'range': [0, 35], 'color': 'rgba(0, 230, 64, 0.3)'},
                                {'range': [35, 70], 'color': 'rgba(240, 255, 0, 0.3)'},
                                {'range': [70, 100], 'color': 'rgba(242, 38, 19, 0.3)'}
                            ],
                        }
                    ))
                    fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with col2:
                    st.subheader("🔍 Vector Analysis Breakdown")
                    categories = ['Profile Data Risk', 'Comments NLP Risk', 'Post Image Risk']
                    scores = [p_acc * 100, p_comm * 100, p_img * 100]
                    
                    fig_bar = go.Figure(go.Bar(
                        x=scores,
                        y=categories,
                        orientation='h',
                        marker_color=['#2ca02c', '#ff7f0e', '#d62728']
                    ))
                    fig_bar.update_layout(xaxis=dict(range=[0, 100]), height=300)
                    st.plotly_chart(fig_bar, use_container_width=True)

                st.write("---")
                if final_score > 0.5:
                    st.error(f"🚨 **CRITICAL ALERT:** This account shows suspicious telemetry pattern matching automation bots.")
                else:
                    st.success(f"✅ **CLEAN RECORD:** No malicious or automated payload footprint found on this node.")

                # --- NEW FEATURE: THREAT REASONING EXPLANATION BOX ---
                st.subheader("💡 AI Diagnostics & Threat Explanation")
                
                with st.container():
                    st.info("Below are the exact parameters and triggers that influenced the AI model's final confidence score.")
                    
                    # 1. Profile Explanations
                    st.markdown("**1. Profile Metadata Analysis Insights:**")
                    if explanation["account"]:
                        for reason in explanation["account"]:
                            st.write(f"❌ {reason}")
                    else:
                        st.write("✅ All profile structure and ratio parameters are well within organic baselines.")
                    
                    # 2. Text/Comments Explanations
                    st.markdown("**2. Natural Language Processing (NLP) Comments Scan:**")
                    if explanation["comments"]:
                        for reason in explanation["comments"]:
                            st.write(f"❌ {reason}")
                    else:
                        st.write("✅ Text streams parsed clean. No automated marketing hooks or scam tokens captured.")
                        
                    # 3. Image Explanations
                    st.markdown("**3. Computer Vision & OCR Post Content Scan:**")
                    for reason in explanation["image"]:
                        if "detected" in reason:
                            st.write(f"❌ {reason}")
                        else:
                            st.write(f"✅ {reason}")

                st.write("---")
                with st.expander("📝 View Telemetry Data Payload"):
                    st.write("**Followers Check:**", data["followers"], " | **Following Check:**", data["following"])
                    st.write("**Extracted Text Matrix:**", data["comments"])
                    if data["image_url"]:
                        st.image(data["image_url"], caption="Scanned Post Attachment Instance", width=250)
            else:
                st.error("Could not fetch data. Server offline or link broken.")
    else:
        st.warning("Please input a handle node first.")

st.write("---")
st.subheader("📜 Recent Cyber Audit Logs (Database Records)")
raw_logs = get_all_logs()

if raw_logs:
    df = pd.DataFrame(raw_logs, columns=["Username Handle", "Threat Score (%)", "Scan Timestamp"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No scans recorded in the database yet.")