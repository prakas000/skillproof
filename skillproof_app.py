import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import plotly.graph_objects as go
import json
import re
import hashlib
import time

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SkillProof — Prove What You Know",
    layout="wide",
    page_icon="⬡",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  BRAND ASSETS & LOGOS
# ─────────────────────────────────────────────
LOGOS = {
    "linkedin":  "https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg",
    "indeed":    "https://www.vectorlogo.zone/logos/indeed/indeed-icon.svg",
    "glassdoor": "https://www.vectorlogo.zone/logos/glassdoor/glassdoor-icon.svg",
    "google":    "https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg",
    "naukri":    "https://static.naukimg.com/s/4/100/i/naukri_Logo.png",
    "wellfound": "https://asset.brandfetch.io/idTuUB0GIy/ideiX9v3m1.svg",
}

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Instrument+Sans:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Instrument Sans', sans-serif; }

.stApp {
    background: #05070f;
    color: #dde4f0;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,200,150,0.07) 0%, transparent 70%),
        linear-gradient(180deg, #05070f 0%, #080c18 100%);
}

/* Sidebar History Styling */
.hist-card {
    padding: 12px; 
    border-radius: 8px; 
    margin-bottom: 8px; 
    background: #080c18; 
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.2s;
}
.hist-card:hover { border-color: rgba(0,200,150,0.3); }
.hist-active { border-left: 3px solid #00c896; background: rgba(0,200,150,0.04); }

/* Other UI Components */
.sp-card { background: #080c18; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 26px; margin-bottom: 20px; position: relative; }
.sp-section { font-family: 'Syne', sans-serif; font-size: 0.72rem; font-weight: 700; color: #00c896; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 18px; display: flex; align-items: center; gap: 10px; }
.sp-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-family: 'Space Mono', monospace; font-size: 0.62rem; font-weight: 700; background: rgba(0,200,150,0.07); color: #00c896; border: 1px solid rgba(0,200,150,0.2); }
.sp-dot { width: 5px; height: 5px; border-radius: 50%; background: #00c896; animation: blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* CTA Buttons */
.stButton > button { background: linear-gradient(135deg, #00c896 0%, #00956e 100%) !important; color: #05070f !important; border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# (Insert standard SVG Logo, Helper functions like verdict, delta_class, and get_text_from_pdf here from previous version)

# ─────────────────────────────────────────────
#  INIT SESSION STATE
# ─────────────────────────────────────────────
state_keys = {
    "phase": 0, 
    "chat_history": [], 
    "assessment_history": [], 
    "final_data": None,
    "current_skill_idx": 0,
    "current_q_idx": 0,
    "skill_scores": [],
    "viewing_id": None
}
for key, default in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  SIDEBAR (History Management)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='text-align:center; padding:20px 0;'>⬡ <b>SkillProof</b></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sp-section'>Past Assessments</div>", unsafe_allow_html=True)
    
    if not st.session_state.assessment_history:
        st.markdown("<div style='font-size:0.7rem; color:#2a3a52; padding:10px;'>No history found.</div>", unsafe_allow_html=True)
    else:
        for entry in st.session_state.assessment_history:
            is_active = st.session_state.viewing_id == entry["id"]
            active_cls = "hist-active" if is_active else ""
            
            st.markdown(f"""
            <div class="hist-card {active_cls}">
                <div style='font-size:0.75rem; font-weight:700; color:#dde4f0;'>{entry['role']}</div>
                <div style='display:flex; justify-content:space-between; margin-top:4px;'>
                    <span style='font-family:Space Mono; font-size:0.65rem; color:#00c896;'>{entry['score']}%</span>
                    <span style='font-size:0.6rem; color:#2a3a52;'>{entry['date']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"View report", key=f"btn_{entry['id']}"):
                st.session_state.final_data = entry["data"]
                st.session_state.phase = 2
                st.session_state.viewing_id = entry["id"]
                st.rerun()

    if st.session_state.assessment_history:
        if st.button("✕ Clear All History"):
            st.session_state.assessment_history = []
            st.rerun()

# ─────────────────────────────────────────────
#  PHASE 1 (INTERVIEW LOOP) - RENDERING FIX
# ─────────────────────────────────────────────
if st.session_state.phase == 1:
    # ... (Question display logic) ...
    
    _eval_ph = st.empty()
    
    if prompt := st.chat_input("Type your answer here..."):
        # RENDERING FIX: The "calibrating score" UI card
        _eval_ph.markdown(f"""
        <div class="sp-card" style="padding:15px; border-color:rgba(0,200,150,0.3); background:rgba(0,200,150,0.03);">
            <div class="sp-pill"><div class="sp-dot"></div>ANALYSING RESPONSE</div>
            <div style="font-size:0.85rem; color:#dde4f0; margin-top:8px;">
                Hold on a moment, reading your answer... <b>calibrating score</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ... (Call LLM for evaluation) ...
        # (Assuming score is returned and interview finishes)

# ─────────────────────────────────────────────
#  PHASE 2 (RESULTS) - AUTO-SAVE TO HISTORY
# ─────────────────────────────────────────────
elif st.session_state.phase == 2:
    fd = st.session_state.final_data
    
    # Save to history if this is a new assessment
    current_id = st.session_state.get("current_assessment_id")
    if current_id and not any(h["id"] == current_id for h in st.session_state.assessment_history):
        history_entry = {
            "id": current_id,
            "role": fd.get("role", "Assessment"),
            "score": fd.get("score", 0),
            "date": time.strftime("%d %b"),
            "data": fd
        }
        st.session_state.assessment_history.insert(0, history_entry)
        st.session_state.viewing_id = current_id

    # ... (Rest of your Dashboard rendering code) ...
