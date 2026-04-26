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
#  BRAND ASSETS
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
#  GLOBAL CSS — SkillProof design system
#  Aesthetic: Precision instrument / Lab terminal
#  Fonts: Syne (display) + Space Mono (data)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Instrument+Sans:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Instrument Sans', sans-serif; }

/* ── App shell ── */
.stApp {
    background: #05070f;
    color: #dde4f0;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,200,150,0.07) 0%, transparent 70%),
        linear-gradient(180deg, #05070f 0%, #080c18 100%);
}
.main .block-container { padding: 2rem 2.5rem 5rem; max-width: 1440px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #070a14;
    border-right: 1px solid rgba(0,200,150,0.12);
}
[data-testid="stSidebar"] * { color: #8fa3c0 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: #0d1220;
    border: 1px solid rgba(0,200,150,0.2);
    color: #dde4f0 !important;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
}

/* ── Logo hex SVG ── */
.sp-logo-wrap {
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 32px;
    padding-bottom: 28px;
    border-bottom: 1px solid rgba(0,200,150,0.1);
}
.sp-hex {
    width: 52px; height: 52px;
    flex-shrink: 0;
}
.sp-wordmark { font-family: 'Syne', sans-serif; }
.sp-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: #f0f6ff;
    letter-spacing: -0.02em;
    line-height: 1;
}
.sp-title span { color: #00c896; }
.sp-tagline {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #4a6280;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 5px;
}

/* ── Cards ── */
.sp-card {
    background: #080c18;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 26px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.sp-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(0,200,150,0.03) 0%, transparent 60%);
    pointer-events: none;
}

/* ── Section titles ── */
.sp-section {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #00c896;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sp-section::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(0,200,150,0.15);
}

/* ── Phase stepper ── */
.phase-bar {
    display: flex;
    gap: 0;
    margin-bottom: 28px;
    background: #0d1220;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    overflow: hidden;
}
.phase-step {
    flex: 1;
    padding: 14px 16px;
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #2a3a52;
    text-transform: uppercase;
    border-right: 1px solid rgba(255,255,255,0.04);
    transition: all 0.3s;
    position: relative;
}
.phase-step:last-child { border-right: none; }
.phase-step.active {
    background: rgba(0,200,150,0.08);
    color: #00c896;
}
.phase-step.done {
    background: rgba(0,200,150,0.04);
    color: #006b50;
}
.phase-step.active::before {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: #00c896;
}
.phase-num {
    display: block;
    font-size: 1.1rem;
    margin-bottom: 3px;
}

/* ── Chat bubbles ── */
.chat-wrap { display: flex; flex-direction: column; gap: 14px; margin-bottom: 20px; }
.bubble {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    max-width: 88%;
}
.bubble.agent { align-self: flex-start; }
.bubble.user  { align-self: flex-end; flex-direction: row-reverse; }
.bubble-avatar {
    width: 32px; height: 32px;
    border-radius: 8px;
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
}
.bubble.agent .bubble-avatar { background: rgba(0,200,150,0.12); color: #00c896; border: 1px solid rgba(0,200,150,0.25); }
.bubble.user  .bubble-avatar { background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.25); }
.bubble-body {
    background: #0d1220;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 0.88rem;
    line-height: 1.65;
    color: #c8d6e8;
}
.bubble.agent .bubble-body { border-top-left-radius: 4px; border-left-color: rgba(0,200,150,0.2); }
.bubble.user  .bubble-body { border-top-right-radius: 4px; border-right-color: rgba(99,102,241,0.2); background: #0c0f1e; }
.bubble-skill-tag {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #00c896;
    background: rgba(0,200,150,0.08);
    border: 1px solid rgba(0,200,150,0.2);
    border-radius: 4px;
    padding: 2px 7px;
    margin-bottom: 6px;
    letter-spacing: 0.08em;
}

/* ── Score display ── */
.score-hex-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px 0 6px;
}
.score-big {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    color: #00c896;
    line-height: 1;
    letter-spacing: -0.04em;
}
.score-sublabel {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: #2a3a52;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 6px;
}
.score-verdict {
    margin-top: 14px;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 18px;
    border-radius: 999px;
    border: 1px solid;
}
.v-low    { color: #f87171; border-color: #7f1d1d; background: #1a0505; }
.v-mid    { color: #fbbf24; border-color: #78350f; background: #180e02; }
.v-high   { color: #34d399; border-color: #065f46; background: #011810; }
.v-elite  { color: #a5b4fc; border-color: #3730a3; background: #06051a; }

/* ── Skill delta tag ── */
.delta-tag {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 11px;
    border-radius: 5px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    margin: 3px;
    border: 1px solid;
}
.d-crit   { color: #f87171; border-color: #7f1d1d; background: #1a0505; }
.d-high   { color: #fb923c; border-color: #9a3412; background: #180a02; }
.d-med    { color: #fbbf24; border-color: #92400e; background: #180e02; }
.d-ok     { color: #34d399; border-color: #065f46; background: #011810; }

/* ── Skill table ── */
.sp-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
.sp-table th {
    padding: 9px 14px;
    background: #0d1220;
    color: #00c896;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    text-align: left;
    border-bottom: 1px solid rgba(0,200,150,0.12);
}
.sp-table td {
    padding: 11px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #8fa3c0;
    vertical-align: top;
}
.sp-table tr:hover td { background: rgba(0,200,150,0.02); }
.sp-table tr:last-child td { border-bottom: none; }
.gap-bar-bg { background: #111827; border-radius: 3px; height: 5px; width: 80px; overflow: hidden; margin-top: 4px; }
.gap-bar    { height: 5px; border-radius: 3px; }

/* ── Interview Q cards ── */
.iq-card {
    background: #0a0e1c;
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 2px solid #00c896;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.iq-meta {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: #00c896;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.iq-q { font-size: 0.92rem; color: #dde4f0; font-weight: 500; margin-bottom: 12px; line-height: 1.5; }
.iq-alabel {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: #34d399;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.iq-a { font-size: 0.82rem; color: #64748b; line-height: 1.65; }
.iq-tip { font-size: 0.78rem; color: #d97706; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.04); }

/* ── Roadmap ── */
.rm-day {
    display: flex; gap: 14px;
    margin-bottom: 16px;
    align-items: flex-start;
}
.rm-badge {
    flex-shrink: 0;
    width: 42px; height: 42px;
    border-radius: 8px;
    background: #0d1220;
    border: 1px solid rgba(0,200,150,0.18);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: #00c896;
    text-align: center;
    line-height: 1.3;
}
.rm-topic { font-size: 0.88rem; font-weight: 600; color: #dde4f0; margin-bottom: 3px; }
.rm-act   { font-size: 0.78rem; color: #3a5070; line-height: 1.5; }
.rm-res a {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 10px;
    background: #0d1220;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 5px;
    font-size: 0.72rem;
    color: #00a07a;
    text-decoration: none;
    margin: 3px 3px 0 0;
    transition: all 0.15s;
}
.rm-res a:hover { background: rgba(0,200,150,0.06); border-color: rgba(0,200,150,0.25); color: #00c896; }

/* ── Job links ── */
.jb-btn {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 15px;
    background: #0d1220;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    text-decoration: none;
    color: #8fa3c0;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 8px;
    transition: all 0.18s;
}
.jb-btn:hover { background: rgba(0,200,150,0.05); border-color: rgba(0,200,150,0.25); color: #dde4f0; text-decoration: none; }
.jb-btn img { width: 20px; height: 20px; object-fit: contain; }

/* ── CTA button ── */
.stButton > button {
    background: linear-gradient(135deg, #00c896 0%, #00956e 100%) !important;
    color: #05070f !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px 28px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    width: 100% !important;
    transition: all 0.2s !important;
    box-shadow: 0 0 24px rgba(0,200,150,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 32px rgba(0,200,150,0.4) !important;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #0d1220 !important;
    color: #dde4f0 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.86rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(0,200,150,0.4) !important;
    box-shadow: 0 0 0 2px rgba(0,200,150,0.1) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #0d1220;
    border: 1px dashed rgba(0,200,150,0.2);
    border-radius: 8px;
    padding: 8px;
}

/* ── Misc ── */
hr { border-color: rgba(255,255,255,0.05) !important; }
.stSpinner > div { border-top-color: #00c896 !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.streamlit-expanderHeader {
    background: #0d1220 !important;
    color: #00c896 !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important;
}

/* ── Status pill ── */
.sp-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    background: rgba(0,200,150,0.07);
    color: #00c896;
    border: 1px solid rgba(0,200,150,0.2);
}
.sp-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #00c896;
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Proof score comparison ── */
.proof-compare {
    display: flex; gap: 12px; margin-top: 12px;
}
.proof-box {
    flex: 1;
    background: #0d1220;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
}
.proof-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1;
}
.proof-lbl {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    color: #2a3a52;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 5px;
}

/* ── Calibration indicator ── */
.calibration-bar {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px;
    background: #0d1220;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    margin-bottom: 14px;
    font-size: 0.8rem;
}
.cal-icon { font-size: 1rem; }
.cal-label { color: #4a6280; font-size: 0.78rem; flex: 1; }
.cal-score {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
}
.cal-green { color: #00c896; }
.cal-amber { color: #fbbf24; }
.cal-red   { color: #f87171; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SVG LOGO — Fingerprint resolving into a checkmark
#  Concept: identity verification + proof of skill
#  The ridgelines of a fingerprint curve inward and
#  the central whorl morphs into a clean tick mark —
#  visually encoding "your identity, verified".
# ─────────────────────────────────────────────
SKILLPROOF_LOGO_SVG = """
<svg viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg" class="sp-hex">
  <defs>
    <radialGradient id="fpGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00c896" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#00c896" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- glow backdrop -->
  <circle cx="28" cy="28" r="26" fill="url(#fpGlow)"/>

  <!-- outer ring -->
  <circle cx="28" cy="28" r="25" stroke="#00c896" stroke-width="1" stroke-opacity="0.18"/>

  <!-- fingerprint ridgelines — concentric open arcs, each slightly offset
       to mimic the loop/whorl pattern of a real fingerprint -->
  <!-- ridge 1 — outermost -->
  <path d="M 10 34 Q 10 8 28 8 Q 46 8 46 34" stroke="#00c896" stroke-width="1.4" stroke-opacity="0.35" fill="none" stroke-linecap="round"/>
  <!-- ridge 2 -->
  <path d="M 13 36 Q 13 12 28 12 Q 43 12 43 36" stroke="#00c896" stroke-width="1.4" stroke-opacity="0.45" fill="none" stroke-linecap="round"/>
  <!-- ridge 3 -->
  <path d="M 16 37 Q 16 16 28 16 Q 40 16 40 37" stroke="#00c896" stroke-width="1.4" stroke-opacity="0.55" fill="none" stroke-linecap="round"/>
  <!-- ridge 4 -->
  <path d="M 19 38 Q 19 20 28 20 Q 37 20 37 38" stroke="#00c896" stroke-width="1.5" stroke-opacity="0.65" fill="none" stroke-linecap="round"/>
  <!-- ridge 5 — innermost, broken in centre to make room for check -->
  <path d="M 22 38 Q 22 23 28 23" stroke="#00c896" stroke-width="1.5" stroke-opacity="0.8" fill="none" stroke-linecap="round"/>
  <path d="M 28 23 Q 34 23 34 38" stroke="#00c896" stroke-width="1.5" stroke-opacity="0.8" fill="none" stroke-linecap="round"/>

  <!-- checkmark — sits at the whorl centre, crisp and bold -->
  <!-- left arm of tick -->
  <line x1="22" y1="30" x2="26.5" y2="35" stroke="#00c896" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- right arm of tick (longer) -->
  <line x1="26.5" y1="35" x2="35" y2="24" stroke="#00c896" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- small glow dot at tick apex -->
  <circle cx="26.5" cy="35" r="1.8" fill="#00c896" opacity="0.7"/>
</svg>
"""

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_text_from_pdf(file) -> str:
    try:
        reader = PdfReader(file)
        return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except Exception:
        return ""

def input_fingerprint(jd: str, resume: str) -> str:
    return hashlib.md5((jd.strip() + resume.strip()).encode()).hexdigest()

def verdict(score: int):
    if score < 50:  return "v-low",  "Needs Development"
    if score < 70:  return "v-mid",  "Emerging Candidate"
    if score < 85:  return "v-high", "Strong Candidate"
    return "v-elite", "Elite Candidate"

def delta_class(gap: int):
    if gap >= 5: return "d-crit", "Critical"
    if gap >= 3: return "d-high", "High"
    if gap >= 1: return "d-med",  "Medium"
    return "d-ok", "Proficient"

def gap_color(gap: int) -> str:
    if gap >= 5: return "#f87171"
    if gap >= 3: return "#fb923c"
    if gap >= 1: return "#fbbf24"
    return "#34d399"

def make_gauge(score: int) -> go.Figure:
    clr = "#f87171" if score < 50 else "#fbbf24" if score < 70 else "#34d399" if score < 85 else "#a5b4fc"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 34, "color": "#dde4f0", "family": "Syne"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#1e2d3d",
                     "tickfont": {"color": "#2a3a52", "size": 10}, "nticks": 6},
            "bar": {"color": clr, "thickness": 0.26},
            "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
            "steps": [
                {"range": [0, 50],   "color": "#1a0505"},
                {"range": [50, 70],  "color": "#180e02"},
                {"range": [70, 85],  "color": "#011810"},
                {"range": [85, 100], "color": "#06051a"},
            ],
            "threshold": {"line": {"color": clr, "width": 3}, "thickness": 0.8, "value": score},
        }
    ))
    fig.update_layout(
        height=210, margin=dict(l=16, r=16, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Syne"},
    )
    return fig

def make_bar_chart(skills: list) -> go.Figure:
    names    = [s["name"] for s in skills]
    claimed  = [s.get("claimed", s["current"]) for s in skills]
    proven   = [s["current"] for s in skills]
    required = [s["required"] for s in skills]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Resume Claim", x=names, y=claimed,
        marker_color="rgba(99,102,241,0.5)", marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Claimed: %{y}/10<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Proven Level", x=names, y=proven,
        marker_color="#00c896", marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Proven: %{y}/10<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Required", x=names, y=required,
        marker_color="rgba(251,191,36,0.45)", marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Required: %{y}/10<extra></extra>"
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center",
                    font=dict(color="#4a6280", size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(tickfont=dict(color="#4a6280", size=10), gridcolor="rgba(0,0,0,0)", zeroline=False),
        yaxis=dict(title="Score /10", tickfont=dict(color="#4a6280", size=10),
                   gridcolor="rgba(0,200,150,0.07)", zeroline=False, range=[0, 11]),
        font=dict(family="Instrument Sans"),
    )
    return fig

def make_radar(skills: list) -> go.Figure:
    cats     = [s["name"] for s in skills] + [skills[0]["name"]]
    proven   = [s["current"] for s in skills] + [skills[0]["current"]]
    required = [s["required"] for s in skills] + [skills[0]["required"]]
    claimed  = [s.get("claimed", s["current"]) for s in skills] + [skills[0].get("claimed", skills[0]["current"])]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=required, theta=cats, fill="toself", name="Required",
        line_color="#fbbf24", fillcolor="rgba(251,191,36,0.06)"))
    fig.add_trace(go.Scatterpolar(r=claimed, theta=cats, fill="toself", name="Resume Claim",
        line_color="rgba(99,102,241,0.6)", fillcolor="rgba(99,102,241,0.06)", line_dash="dot"))
    fig.add_trace(go.Scatterpolar(r=proven, theta=cats, fill="toself", name="Proven",
        line_color="#00c896", fillcolor="rgba(0,200,150,0.1)"))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,10], tickfont=dict(color="#2a3a52", size=8), gridcolor="rgba(255,255,255,0.04)"),
            angularaxis=dict(tickfont=dict(color="#4a6280", size=9), gridcolor="rgba(255,255,255,0.04)"),
        ),
        showlegend=True,
        legend=dict(font=dict(color="#4a6280", size=10), bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        height=290, margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Instrument Sans"),
    )
    return fig

def make_learning_curve() -> go.Figure:
    import math
    xs = list(range(0, 15))
    flat  = [40] * 15
    curve = [40 + 44 * (1 - math.exp(-0.25 * x)) for x in xs]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=flat, name="No Training",
        line=dict(color="#2a3a52", dash="dot", width=1.5)))
    fig.add_trace(go.Scatter(x=xs, y=curve, name="With SkillProof Roadmap",
        line=dict(color="#00c896", width=2.5),
        fill="tonexty", fillcolor="rgba(0,200,150,0.06)"))
    fig.add_vline(x=7, line_dash="dash", line_color="#fbbf24",
                  annotation_text="Week 1", annotation_font_color="#fbbf24")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=190, margin=dict(l=0, r=0, t=8, b=0),
        xaxis=dict(title="Day", tickfont=dict(color="#4a6280", size=10), gridcolor="rgba(0,200,150,0.05)", zeroline=False),
        yaxis=dict(title="Readiness %", tickfont=dict(color="#4a6280", size=10), gridcolor="rgba(0,200,150,0.05)", range=[0,100]),
        legend=dict(font=dict(color="#4a6280", size=10), bgcolor="rgba(0,0,0,0)"),
        font=dict(family="Instrument Sans"),
    )
    return fig


# ─────────────────────────────────────────────
#  PROMPTS
# ─────────────────────────────────────────────

EXTRACT_SKILLS_PROMPT = """You are a technical recruiter. Extract the 6 most critical skills from this Job Description.

JD:
{jd}

RESUME (for context only — do not score yet):
{resume}

Return JSON only:
{{
  "role": "<most specific job title>",
  "skills": [
    {{
      "name": "<skill name, 1-3 words>",
      "claimed_level": <1-10 inferred from resume>,
      "required_level": <1-10 required by JD>,
      "probe_depth": "<beginner|intermediate|advanced>"
    }}
  ]
}}"""

GENERATE_PROBE_PROMPT = """You are a friendly but thorough hiring manager interviewing a candidate for a {depth}-level role.
You want to understand how well they know {skill_name} — but you want to have a natural conversation, not an exam.

Role context: the candidate is applying for a position where {skill_name} is important.
Their resume suggests a level of {claimed}/10. The role needs {required}/10.

Write exactly 2 interview questions about {skill_name}:
- Q1: A warm, open question a real hiring manager would ask — something like "Can you walk me through how you've used X?" or "How would you approach Y?" — conversational, not textbook
- Q2: A slightly more specific follow-up that reveals whether they really understand it in practice — still human in tone, not a quiz question

Rules:
- Sound like a person, not an assessment tool
- No trick questions, no jargon overload
- Short and clear — one question per entry, not a paragraph
- Match tone to depth: beginner = casual and friendly, intermediate = professional, advanced = peer-level technical

Return JSON only:
[
  {{"q": "<question>", "type": "Experience"}},
  {{"q": "<question>", "type": "Practical"}}
]"""

EVALUATE_ANSWER_PROMPT = """You are a hiring manager who just heard this answer in an interview.
React honestly and fairly — like a real person would, not a scoring machine.

Role: hiring manager evaluating {skill_name} proficiency
Required level: {required}/10
Claimed level: {claimed}/10
Question asked: {question}
Candidate's answer: {answer}

Score 1-10 where:
- 1-3: Answer shows little real understanding — vague, generic, or incorrect
- 4-6: Decent answer — shows some familiarity but missing depth or specifics
- 7-8: Good answer — clear understanding, mentions real experience or concrete details
- 9-10: Impressive — specific, nuanced, shows they've actually done this

Be fair. A conversational answer that shows genuine understanding beats a rehearsed but hollow technical answer.
Keep feedback warm and constructive — one or two sentences max, like you'd say it in the room.

Return JSON only:
{{
  "score": <1-10>,
  "signal": "<strong|adequate|weak|incorrect>",
  "feedback": "<1-2 sentence honest but human reaction to the answer>",
  "revealed_gap": "<null or specific knowledge gap revealed>"
}}"""

FINAL_ANALYSIS_PROMPT = """Analyse this candidate using BOTH the resume AND the conversational interview transcript.

SCORING RUBRIC (100 pts):
  A) Proven Technical Skills (from interview) — 50 pts  <- WEIGHT THIS MOST
  B) Domain Transferability                   — 30 pts
  C) Academic Background & Experience         — 20 pts

CRITICAL RULES:
- Interview answers are ground truth. If resume claims X but interview showed Y, use Y.
- Skipped questions are NEUTRAL — do not penalise. Fall back to resume evidence for those skills.
- Do NOT go below 40% unless interview showed complete absence of knowledge.
- Do NOT go above 92%.

JD:
{jd}

RESUME:
{resume}

INTERVIEW TRANSCRIPT:
{transcript}

SKILL CALIBRATION (proven scores from live interview — skipped skills excluded):
{calibration}

SKIPPED SKILLS NOTE:
{skipped_note}

Return JSON only:
{{
  "score": <int 0-100>,
  "resume_score": <int, what score would have been from resume alone>,
  "role": "<most specific relevant job title>",
  "summary": "<2-sentence honest assessment that references specific interview answers>",
  "skills": [
    {{
      "name": "<skill>",
      "claimed": <1-10 from resume>,
      "current": <1-10 proven in interview, or resume-inferred if skipped>,
      "required": <1-10>,
      "evidence": "<brief note — if skipped write: Not assessed in interview, inferred from resume>"
    }}
  ],
  "top_gaps": ["<gap 1>", "<gap 2>", "<gap 3>"],
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "calibration_note": "<1 sentence on how interview matched or differed from resume claims, mention any skipped skills by name>"
}}"""

INTERVIEW_PREP_PROMPT = """Senior technical interviewer. Role: '{role}'. Proven weak areas: {gaps}.

Generate 8 interview Q&As (mix: 2 conceptual, 4 technical, 2 behavioural). Base answers on what a strong candidate would say.

Return JSON only:
[
  {{
    "num": 1,
    "type": "Conceptual",
    "q": "<question>",
    "a": "<2-3 sentence model answer>",
    "tip": "<practical preparation tip>"
  }}
]"""

ROADMAP_PROMPT = """Create a 14-day personalised upskilling roadmap.
Role: '{role}'. Proven weak areas from live interview: {gaps}.
Candidate proven strengths (use for adjacency reasoning): {strengths}.

Prioritise skills by adjacency - how close each gap skill is to what the candidate already knows.
High adjacency skills come first (faster wins). Low adjacency skills come later.

Each day must include a realistic time estimate (most people have 1-2 hrs/day).

Return JSON only:
[
  {{
    "day": 1,
    "topic": "<specific topic>",
    "hours": 1.5,
    "adjacency_note": "<on day 1 of each new skill block: one sentence on why prioritised. null for continuation days>",
    "activities": ["<activity 1>", "<activity 2>"],
    "resources": [
      {{"label": "<platform: title>", "url": "<real URL>", "type": "video|doc|course|github"}}
    ]
  }}
]"""


# ─────────────────────────────────────────────
#  LLM CALL + PARSE
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
#  MULTI-PROVIDER FALLBACK ENGINE
#  Tries each configured provider in order.
#  Silently moves to next on 401, 429, or any error.
#  User never sees which provider is active.
# ─────────────────────────────────────────────

PROVIDERS = [
    {
        "name": "groq",
        "secret_key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
    },
    {
        "name": "qwen",
        "secret_key": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    {
        "name": "openai",
        "secret_key": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
]

def _get_provider_keys() -> list:
    """Read all provider keys from Streamlit secrets. Returns list of active providers."""
    active = []
    for p in PROVIDERS:
        try:
            key = st.secrets.get(p["secret_key"], "").strip()
        except Exception:
            key = ""
        if key:
            active.append({**p, "api_key": key})
    return active

def call_groq(client_unused, user_content: str, temperature: float = 0.0) -> str:
    """
    Multi-provider LLM call with automatic fallback.
    Tries each provider in order: Groq → Qwen → OpenAI.
    Falls back silently on auth errors or rate limits.
    """
    providers = _get_provider_keys()
    if not providers:
        raise ValueError(
            "No API keys configured. Add GROQ_API_KEY, QWEN_API_KEY, or OPENAI_API_KEY "
            "to Streamlit secrets."
        )

    system_prompt = (
        "You are a JSON-only API. "
        "Your ENTIRE response must be valid JSON — either { } or [ ]. "
        "Start immediately with { or [. No markdown, no fences, no preamble, no postamble. "
        "Violation causes critical system failure."
    )

    last_error = None
    for p in providers:
        try:
            client = OpenAI(api_key=p["api_key"], base_url=p["base_url"])
            resp = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_content},
                ],
                model=p["model"],
                temperature=temperature,
                max_tokens=4096,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            err_str = str(e)
            # On auth or rate limit errors try next provider
            if any(code in err_str for code in ["401", "429", "invalid_api_key", "rate_limit", "quota"]):
                last_error = f"{p['name']}: {err_str[:120]}"
                continue
            # On other errors (network, timeout) also try next
            last_error = f"{p['name']}: {err_str[:120]}"
            continue

    raise ValueError(f"All providers failed. Last error: {last_error}")

def parse_json(raw: str):
    if not raw:
        raise ValueError("Empty response.")
    def clean(s):
        s = re.sub(r"```json\s*", "", s)
        s = re.sub(r"```\s*", "", s)
        s = re.sub(r",\s*([\}\]])", r"\1", s)
        return s.strip()
    for attempt in [raw, clean(raw)]:
        try: return json.loads(attempt)
        except: pass
    for pattern in [r"(\{[\s\S]*\})", r"(\[[\s\S]*\])"]:
        m = re.search(pattern, clean(raw))
        if m:
            try: return json.loads(clean(m.group(1)))
            except: pass
    raise ValueError(f"Cannot parse JSON. First 400 chars: {repr(raw[:400])}")

def unwrap(data):
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list): return v
    return data


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:16px 0 24px;'>
      <div style='display:flex; justify-content:center; margin-bottom:10px;'>{SKILLPROOF_LOGO_SVG}</div>
      <div style='font-family:Syne,sans-serif; font-size:1.2rem; font-weight:800; color:#f0f6ff;'>Skill<span style='color:#00c896;'>Proof</span></div>
      <div style='font-family:Space Mono,monospace; font-size:0.58rem; color:#2a3a52; letter-spacing:0.14em; margin-top:4px;'>PROVE WHAT YOU KNOW</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(0,200,150,0.1); margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:Space Mono,monospace; font-size:0.6rem; color:#2a3a52; letter-spacing:0.12em; margin-bottom:10px;">SYSTEM STATUS</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    col_s1.markdown('<div class="sp-pill"><div class="sp-dot"></div> Live</div>', unsafe_allow_html=True)
    col_s2.markdown('<div style="font-family:Space Mono,monospace; font-size:0.6rem; color:#2a3a52; padding-top:5px;">AI-Powered</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.78rem; color:#2a3a52; line-height:1.8;'>
      <b style='color:#3a5070; font-family:Space Mono,monospace; font-size:0.65rem;'>PIPELINE</b><br>
      Phase 1 — Resume Parse<br>
      Phase 2 — Skill Extraction<br>
      Phase 3 — Live Probe Interview<br>
      Phase 4 — Calibrated Scoring<br>
      Phase 5 — Career Report<br><br>
      <b style='color:#3a5070; font-family:Space Mono,monospace; font-size:0.65rem;'>PROBE MODES</b><br>
      ⚡ Quick Scan — 1 Q/skill (~6)<br>
      ⬡ Standard — 2 Q/skill (~12)<br>
      🔬 Deep Probe — 3 Q/skill (~18)<br><br>
      <b style='color:#3a5070; font-family:Space Mono,monospace; font-size:0.65rem;'>SCORING ENGINE</b><br>
      WSS v4 + Interview Calibration<br>
      Resume claims ≠ proven scores<br>
      Interview answers = ground truth<br>
      Auto-fallback: Groq → Qwen → OpenAI
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(0,200,150,0.08); margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:Space Mono,monospace; font-size:0.55rem; color:#1a2535; text-align:center; line-height:1.8;'>
      CATALYST HACKATHON 2025<br>
      DECCAN AI EXPERTS<br>
      QWEN · QWEN-PLUS
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  INIT SESSION STATE
# ─────────────────────────────────────────────
for key in ["phase", "skill_plan", "probe_questions", "chat_history",
            "current_skill_idx", "current_q_idx", "skill_scores",
            "final_data", "interview_data", "roadmap_data"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["skill_plan","probe_questions","final_data","interview_data","roadmap_data"] else ([] if key in ["chat_history","skill_scores"] else 0)

if st.session_state.phase is None:
    st.session_state.phase = 0  # 0=input, 1=probing, 2=results


# ─────────────────────────────────────────────
#  MAIN HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="sp-logo-wrap">
  {SKILLPROOF_LOGO_SVG}
  <div class="sp-wordmark">
    <div class="sp-title">Skill<span>Proof</span></div>
    <div class="sp-tagline">⬡ &nbsp; Conversational AI · Proves Real Proficiency · Not Just Resume Claims</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Phase stepper
phases = ["01 · Input", "02 · Probe", "03 · Score", "04 · Roadmap"]
phase_html = '<div class="phase-bar">'
for i, p in enumerate(phases):
    cls = "active" if i == st.session_state.phase else ("done" if i < st.session_state.phase else "")
    icon = "✓ " if i < st.session_state.phase else ""
    phase_html += f'<div class="phase-step {cls}"><span class="phase-num">{icon}{p}</span></div>'
phase_html += '</div>'
st.markdown(phase_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  PHASE 0 — INPUT
# ═══════════════════════════════════════════
if st.session_state.phase == 0:
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="sp-section">📋 Job Description</div>', unsafe_allow_html=True)
        jd_input = st.text_area("jd", label_visibility="collapsed", height=200,
            placeholder="Paste the full job description here — responsibilities, required skills, qualifications...")
    with c2:
        st.markdown('<div class="sp-section">📄 Resume PDF</div>', unsafe_allow_html=True)
        resume_file = st.file_uploader("resume", label_visibility="collapsed", type=["pdf"])
        if resume_file:
            st.markdown(f'<div style="font-size:0.8rem; color:#00c896; margin-top:6px; font-family:Space Mono,monospace;">✓ {resume_file.name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style='background:rgba(0,200,150,0.04); border:1px solid rgba(0,200,150,0.12); border-radius:10px; padding:16px 20px; margin-bottom:22px;'>
      <div style='font-family:Syne,sans-serif; font-size:0.72rem; font-weight:700; color:#00c896; letter-spacing:0.14em; margin-bottom:8px;'>⬡ WHAT MAKES SKILLPROOF DIFFERENT</div>
      <div style='font-size:0.82rem; color:#3a5070; line-height:1.7;'>
        Unlike tools that read your resume and guess your skill level, SkillProof <b style='color:#4a8a70;'>asks you probing questions</b> for each claimed skill.
        Your live answers override your resume. The final score reflects what you <i>actually know</i> — not what you wrote.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Probe depth selector ──
    st.markdown('<div class="sp-section">⬡ Choose Assessment Depth</div>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    div[data-testid="column"]:has(.probe-card) { cursor: pointer; }
    .probe-card {
        background: #080c18;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 18px 16px;
        text-align: center;
        transition: all 0.18s;
        cursor: pointer;
        height: 100%;
    }
    .probe-card.selected {
        border-color: #00c896;
        background: rgba(0,200,150,0.06);
        box-shadow: 0 0 20px rgba(0,200,150,0.1);
    }
    .probe-icon  { font-size: 1.6rem; margin-bottom: 8px; }
    .probe-name  { font-family: 'Syne', sans-serif; font-size: 0.85rem; font-weight: 700; color: #dde4f0; margin-bottom: 4px; }
    .probe-count { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #00c896; letter-spacing: 0.1em; margin-bottom: 8px; }
    .probe-desc  { font-size: 0.75rem; color: #2a3a52; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

    PROBE_MODES = {
        "Quick Scan":  {"q_per_skill": 1, "total": "~4 questions", "icon": "⚡", "desc": "One focused question per skill across 4 key areas. Best for a fast, efficient assessment.", "depth_override": "beginner", "skill_limit": 4},
        "Standard":    {"q_per_skill": 2, "total": "~12 questions", "icon": "⬡", "desc": "Two calibrated questions per skill — conceptual + practical. Recommended.", "depth_override": None, "skill_limit": 6},
        "Deep Probe":  {"q_per_skill": 3, "total": "~18 questions", "icon": "🔬", "desc": "Three layered questions per skill for high-stakes roles or senior positions.", "depth_override": "advanced", "skill_limit": 6},
    }

    if "probe_mode" not in st.session_state:
        st.session_state.probe_mode = "Standard"

    mc1, mc2, mc3 = st.columns(3, gap="medium")
    for col, (mode_name, mode_cfg) in zip([mc1, mc2, mc3], PROBE_MODES.items()):
        with col:
            selected = st.session_state.probe_mode == mode_name
            border = "#00c896" if selected else "rgba(255,255,255,0.06)"
            bg     = "rgba(0,200,150,0.06)" if selected else "#080c18"
            tick   = "✓ " if selected else ""
            st.markdown(f"""
            <div class="probe-card {'selected' if selected else ''}">
              <div class="probe-icon">{mode_cfg['icon']}</div>
              <div class="probe-name">{tick}{mode_name}</div>
              <div class="probe-count">{mode_cfg['total']}</div>
              <div class="probe-desc">{mode_cfg['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {mode_name}", key=f"mode_{mode_name}",
                         help=mode_cfg["desc"]):
                st.session_state.probe_mode = mode_name
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Show selected mode summary
    sel = PROBE_MODES[st.session_state.probe_mode]
    st.markdown(f"""
    <div style='font-family:Space Mono,monospace; font-size:0.68rem; color:#006b50; text-align:center; margin-bottom:18px; letter-spacing:0.08em;'>
      ⬡ &nbsp; {st.session_state.probe_mode.upper()} MODE SELECTED &nbsp;·&nbsp; {sel['total'].upper()} &nbsp;·&nbsp; {sel['q_per_skill']} PER SKILL
    </div>
    """, unsafe_allow_html=True)

    if st.button("⬡  BEGIN SKILLPROOF ASSESSMENT"):
        if not _get_provider_keys():
            st.error("⚠️  No API keys configured. Add at least one key to Streamlit secrets.")
            st.stop()
        if not jd_input or not jd_input.strip():
            st.error("⚠️  Paste a Job Description.")
            st.stop()
        if not resume_file:
            st.error("⚠️  Upload your Resume PDF.")
            st.stop()
        resume_text = get_text_from_pdf(resume_file)
        if not resume_text:
            st.error("⚠️  Could not extract PDF text. Ensure it is not a scanned image.")
            st.stop()

        with st.spinner("⬡  Extracting skill plan from JD + Resume..."):
            try:
                # provider selected automatically by fallback engine
                raw = call_groq(None, EXTRACT_SKILLS_PROMPT.format(
                    jd=jd_input[:3000], resume=resume_text[:2500]))
                plan = parse_json(raw)
                skills = plan.get("skills", [])

                # Resolve probe mode settings
                sel_mode       = PROBE_MODES[st.session_state.probe_mode]
                q_per_skill    = sel_mode["q_per_skill"]
                depth_override = sel_mode["depth_override"]
                skill_limit    = sel_mode.get("skill_limit", 6)

                # Generate all probe questions upfront, respecting mode
                all_probes = []
                for sk in skills[:skill_limit]:
                    effective_depth = depth_override or sk.get("probe_depth", "intermediate")
                    raw_q = call_groq(None, GENERATE_PROBE_PROMPT.format(
                        skill_name=sk["name"],
                        claimed=sk.get("claimed_level", 5),
                        required=sk.get("required_level", 7),
                        depth=effective_depth
                    ))
                    qs = parse_json(raw_q)
                    if isinstance(qs, list):
                        # Trim to chosen q_per_skill
                        all_probes.append({"skill": sk, "questions": qs[:q_per_skill]})

                st.session_state.skill_plan   = plan
                st.session_state.probe_questions = all_probes
                st.session_state.chat_history = []
                st.session_state.current_skill_idx = 0
                st.session_state.current_q_idx     = 0
                st.session_state.skill_scores = []
                st.session_state["_jd"]     = jd_input
                st.session_state["_resume"] = resume_text
                st.session_state.phase = 1
                st.rerun()
            except Exception as e:
                st.error(f"❌  Skill extraction failed: {e}")


# ═══════════════════════════════════════════
#  PHASE 1 — CONVERSATIONAL PROBING
# ═══════════════════════════════════════════
elif st.session_state.phase == 1:
    probes   = st.session_state.probe_questions or []
    si       = st.session_state.current_skill_idx
    qi       = st.session_state.current_q_idx
    total_skills = len(probes)

    if si >= total_skills:
        # All probes done — move to final analysis
        st.session_state.phase = 2
        st.rerun()

    current_probe = probes[si]
    skill         = current_probe["skill"]
    questions     = current_probe["questions"]
    total_q_this_skill = len(questions)

    # Progress info
    total_questions = sum(len(p["questions"]) for p in probes)
    answered = sum(len(p["questions"]) for p in probes[:si]) + qi
    progress_pct = answered / total_questions if total_questions else 0

    col_chat, col_meta = st.columns([1.6, 1], gap="large")

    with col_meta:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">⬡ Assessment Progress</div>', unsafe_allow_html=True)
        st.progress(progress_pct)
        st.markdown(f"""
        <div style='font-family:Space Mono,monospace; font-size:0.68rem; color:#2a3a52; margin-top:6px; margin-bottom:16px;'>
          {answered}/{total_questions} QUESTIONS COMPLETE
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='font-family:Space Mono,monospace; font-size:0.62rem; color:#00c896; letter-spacing:0.1em; margin-bottom:8px;'>CURRENT SKILL</div>
        <div style='font-family:Syne,sans-serif; font-size:1.1rem; font-weight:700; color:#f0f6ff; margin-bottom:4px;'>{skill["name"]}</div>
        <div style='font-size:0.78rem; color:#2a3a52; margin-bottom:14px;'>Q{qi+1} of {total_q_this_skill} · Skill {si+1}/{total_skills}</div>
        """, unsafe_allow_html=True)

        # Live calibration scores so far
        if st.session_state.skill_scores:
            st.markdown('<div style="font-family:Space Mono,monospace; font-size:0.6rem; color:#2a3a52; letter-spacing:0.1em; margin-bottom:8px;">CALIBRATED SO FAR</div>', unsafe_allow_html=True)
            for sc in st.session_state.skill_scores:
                signal_cls = "cal-green" if sc["score"] >= 7 else ("cal-amber" if sc["score"] >= 5 else "cal-red")
                st.markdown(f"""
                <div class="calibration-bar">
                  <span class="cal-icon">⬡</span>
                  <span class="cal-label">{sc["skill"]}</span>
                  <span class="cal-score {signal_cls}">{sc["score"]}/10</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:0.72rem; color:#1a2535; line-height:1.7; margin-top:12px; border-top:1px solid rgba(255,255,255,0.04); padding-top:12px;">Your live answers are being scored in real-time and will override resume claims in the final report.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chat:
        st.markdown('<div class="sp-card" style="min-height:500px;">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">⬡ Live Probe Interview</div>', unsafe_allow_html=True)

        # Render chat history
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                content = re.sub(r"<[^>]+>", "", str(msg.get("content", ""))).strip()
                if msg["role"] == "agent":
                    skill_tag = ""
                    if msg.get("skill"):
                        skill_tag = f'<div class="bubble-skill-tag">PROBING: {msg["skill"]}</div>'
                    score_tag = ""
                    if msg.get("score"):
                        sig = str(msg.get("signal", "")).upper()
                        sc  = str(msg.get("score", ""))
                        score_tag = f'<div style="font-size:0.72rem;color:#006b50;margin-top:8px;font-family:Space Mono,monospace;">Signal: {sig} · Score: {sc}/10</div>'
                    st.markdown(
                        f'<div class="bubble agent">'
                        f'<div class="bubble-avatar">SP</div>'
                        f'<div class="bubble-body">{skill_tag}{content}{score_tag}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="bubble user">'
                        f'<div class="bubble-avatar">YOU</div>'
                        f'<div class="bubble-body">{content}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        # Ask current question
        if qi < total_q_this_skill:
            current_q = questions[qi]
            q_text = current_q.get("q", "")
            q_type = current_q.get("type", "")

            # Show the question as an agent bubble (not yet in history)
            q_safe = re.sub(r"<[^>]+>", "", q_text).strip()
            st.markdown(
                f'<div class="bubble agent">'
                f'<div class="bubble-avatar">SP</div>'
                f'<div class="bubble-body">'
                f'<div class="bubble-skill-tag">PROBING: {skill["name"]} · {q_type}</div>'
                f'{q_safe}'
                f'</div></div>',
                unsafe_allow_html=True
            )

            answer = st.text_area(
                "Your answer",
                key=f"ans_{si}_{qi}",
                height=110,
                placeholder="Type your answer here — be specific, mention tools, approaches, trade-offs you've encountered..."
            )

            c_sub, c_skip = st.columns([3, 1])
            with c_sub:
                submit = st.button("⬡  Submit Answer", key=f"sub_{si}_{qi}")
            with c_skip:
                skip = st.button("Skip →", key=f"skip_{si}_{qi}")

            if submit and answer.strip():
                with st.spinner("⬡  Evaluating answer..."):
                    try:
                        # provider selected automatically by fallback engine
                        raw_eval = call_groq(None, EVALUATE_ANSWER_PROMPT.format(
                            skill_name=skill["name"],
                            required=skill.get("required_level", 7),
                            claimed=skill.get("claimed_level", 5),
                            question=q_text,
                            answer=answer.strip()
                        ))
                        ev = parse_json(raw_eval)
                        ev_score   = ev.get("score", 5)
                        ev_signal  = ev.get("signal", "adequate")
                        ev_feedback = ev.get("feedback", "Answer recorded.")

                        # Append to chat history — keep feedback text clean, score stored separately
                        st.session_state.chat_history.append({"role": "agent", "content": q_text, "skill": skill["name"]})
                        st.session_state.chat_history.append({"role": "user",  "content": answer.strip()})
                        # Strip any accidental HTML/div tags from model feedback before storing
                        clean_feedback = re.sub(r"<[^>]+>", "", ev_feedback).strip()
                        st.session_state.chat_history.append({
                            "role": "agent",
                            "content": clean_feedback,
                            "score": ev_score,
                            "signal": ev_signal
                        })

                        # Advance
                        next_qi = qi + 1
                        if next_qi >= total_q_this_skill:
                            # Average score for this skill
                            recent_scores = [m["score"] for m in st.session_state.chat_history if m.get("score") is not None]
                            avg = recent_scores[-1] if recent_scores else 5
                            st.session_state.skill_scores.append({"skill": skill["name"], "score": avg})
                            st.session_state.current_skill_idx += 1
                            st.session_state.current_q_idx = 0
                        else:
                            st.session_state.current_q_idx = next_qi

                        st.rerun()
                    except Exception as e:
                        st.error(f"Evaluation error: {e}")

            if skip:
                st.session_state.chat_history.append({"role": "agent", "content": q_text, "skill": skill["name"]})
                st.session_state.chat_history.append({"role": "user", "content": "[Not assessed — question skipped]"})
                next_qi = qi + 1
                if next_qi >= total_q_this_skill:
                    # Mark as skipped — excluded from calibration scoring, noted in report
                    st.session_state.skill_scores.append({
                        "skill": skill["name"],
                        "score": None,
                        "skipped": True
                    })
                    st.session_state.current_skill_idx += 1
                    st.session_state.current_q_idx = 0
                else:
                    st.session_state.current_q_idx = next_qi
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  PHASE 2 — RESULTS (Scoring + Report)
# ═══════════════════════════════════════════
elif st.session_state.phase == 2:
    # Run final analysis once
    if st.session_state.final_data is None:
        try:
            # provider selected automatically by fallback engine

            # Build transcript
            transcript_lines = []
            for msg in st.session_state.chat_history:
                role_label = "INTERVIEWER" if msg["role"] == "agent" else "CANDIDATE"
                line = f"{role_label}: {msg['content']}"
                if msg.get("score"):
                    line += f" [Evaluator score: {msg['score']}/10, signal: {msg.get('signal','')}]"
                transcript_lines.append(line)
            transcript = "\n".join(transcript_lines)

            # Separate scored vs skipped skills for calibration note
            scored   = [s for s in st.session_state.skill_scores if not s.get("skipped")]
            skipped  = [s["skill"] for s in st.session_state.skill_scores if s.get("skipped")]
            calibration = json.dumps(scored)
            skipped_note = f"Skills NOT assessed (candidate skipped): {', '.join(skipped)}" if skipped else "All skills assessed."

            with st.spinner("⬡  Running final calibrated analysis..."):
                raw_final = call_groq(None, FINAL_ANALYSIS_PROMPT.format(
                    jd=st.session_state["_jd"][:3000],
                    resume=st.session_state["_resume"][:2500],
                    transcript=transcript[:4000],
                    calibration=calibration,
                    skipped_note=skipped_note
                ))
                st.session_state.final_data = parse_json(raw_final)

            with st.spinner("⬡  Generating interview prep..."):
                fd = st.session_state.final_data
                raw_int = call_groq(None, INTERVIEW_PREP_PROMPT.format(
                    role=fd.get("role", "the role"),
                    gaps=", ".join(fd.get("top_gaps", []))
                ))
                idata = parse_json(raw_int)
                st.session_state.interview_data = unwrap(idata) if isinstance(idata, (list,dict)) else []

            with st.spinner("⬡  Building 14-day roadmap..."):
                raw_road = call_groq(None, ROADMAP_PROMPT.format(
                    role=fd.get("role", "the role"),
                    gaps=", ".join(fd.get("top_gaps", [])),
                    strengths=", ".join(fd.get("strengths", []))
                ))
                rdata = parse_json(raw_road)
                st.session_state.roadmap_data = unwrap(rdata) if isinstance(rdata, (list,dict)) else []

        except Exception as e:
            st.error(f"❌  Final analysis failed: {e}")
            st.stop()

    fd        = st.session_state.final_data
    score     = int(fd.get("score", 0))
    r_score   = int(fd.get("resume_score", score))
    role      = fd.get("role", "N/A")
    skills    = fd.get("skills", [])
    gaps      = fd.get("top_gaps", [])
    strengths = fd.get("strengths", [])
    summary   = fd.get("summary", "")
    cal_note  = fd.get("calibration_note", "")

    v_cls, v_lbl = verdict(score)
    q_role = role.replace(" ", "%20")

    st.markdown('<div style="font-family:Space Mono,monospace; font-size:0.62rem; color:#006b50; letter-spacing:0.14em; margin-bottom:20px;">⬡ ASSESSMENT COMPLETE — CALIBRATED REPORT BELOW</div>', unsafe_allow_html=True)

    # ROW 1: Score | Summary | Jobs
    col_score, col_sum, col_jobs = st.columns([1, 1.3, 1], gap="medium")

    with col_score:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">Proof Score</div>', unsafe_allow_html=True)
        st.plotly_chart(make_gauge(score), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"""
        <div style='text-align:center; margin-top:-6px;'>
          <span class='score-verdict {v_cls}'>{v_lbl}</span>
        </div>
        <div style='font-family:Syne,sans-serif; font-size:0.85rem; font-weight:600; color:#4a6280; text-align:center; margin-top:10px;'>{role}</div>
        """, unsafe_allow_html=True)

        # Resume vs Proven comparison
        delta = score - r_score
        delta_str = f"+{delta}" if delta >= 0 else str(delta)
        delta_clr = "#34d399" if delta >= 0 else "#f87171"
        st.markdown(f"""
        <div class="proof-compare">
          <div class="proof-box">
            <div class="proof-num" style="color:#4a6280;">{r_score}%</div>
            <div class="proof-lbl">Resume Only</div>
          </div>
          <div class="proof-box">
            <div class="proof-num" style="color:#00c896;">{score}%</div>
            <div class="proof-lbl">Proof Score</div>
          </div>
        </div>
        <div style='text-align:center; font-family:Space Mono,monospace; font-size:0.72rem; margin-top:8px; color:{delta_clr};'>
          Interview delta: {delta_str} pts
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_sum:
        st.markdown('<div class="sp-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">Assessment Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#8fa3c0; font-size:0.86rem; line-height:1.7; margin-bottom:14px;">{summary}</p>', unsafe_allow_html=True)

        if cal_note:
            st.markdown(f"""
            <div style='background:rgba(0,200,150,0.04); border:1px solid rgba(0,200,150,0.1); border-radius:7px; padding:10px 13px; margin-bottom:14px; font-size:0.8rem; color:#006b50; font-style:italic;'>
              ⬡ {cal_note}
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="font-family:Space Mono,monospace; font-size:0.6rem; color:#34d399; letter-spacing:0.1em; margin-bottom:8px;">PROVEN STRENGTHS</div>', unsafe_allow_html=True)
        for s in strengths:
            st.markdown(f'<div style="font-size:0.8rem; color:#4a6280; padding:2px 0;">▸ {s}</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Space Mono,monospace; font-size:0.6rem; color:#f87171; letter-spacing:0.1em; margin-top:12px; margin-bottom:8px;">GAP AREAS</div>', unsafe_allow_html=True)
        for g in gaps:
            st.markdown(f'<div style="font-size:0.8rem; color:#4a6280; padding:2px 0;">▸ {g}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_jobs:
        st.markdown('<div class="sp-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">Live Job Search</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.78rem; color:#2a3a52; margin-bottom:12px;">Openings for <b style="color:#00c896;">{role}</b></div>', unsafe_allow_html=True)
        platforms = [
            ("linkedin",  "LinkedIn Jobs",  f"https://www.linkedin.com/jobs/search/?keywords={q_role}"),
            ("indeed",    "Indeed",         f"https://www.indeed.com/jobs?q={q_role}"),
            ("glassdoor", "Glassdoor",      f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={q_role}"),
            ("google",    "Google Jobs",    f"https://www.google.com/search?q={q_role}+jobs+hiring"),
            ("naukri",    "Naukri.com",     f"https://www.naukri.com/{q_role.replace('%20','-').lower()}-jobs"),
            ("wellfound", "Wellfound",      f"https://wellfound.com/jobs?q={q_role}"),
        ]
        for key, label, url in platforms:
            st.markdown(
                f'<a href="{url}" target="_blank" class="jb-btn">'
                f'<img src="{LOGOS[key]}" onerror="this.style.display=\'none\'">'
                f'{label} →</a>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ROW 2: Skill Gap Table
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    st.markdown('<div class="sp-section">Calibrated Skill Analysis — Proven vs Claimed vs Required</div>', unsafe_allow_html=True)

    tags_html = ""
    for sk in skills:
        gap_val = sk.get("required", 7) - sk.get("current", 5)
        dc, dl = delta_class(gap_val)
        tags_html += f'<span class="delta-tag {dc}">{sk["name"]} — {dl}</span>'
    st.markdown(f'<div style="margin-bottom:16px;">{tags_html}</div>', unsafe_allow_html=True)

    rows = ""
    for sk in skills:
        claimed   = sk.get("claimed", sk.get("current", 5))
        proven    = sk.get("current", 5)
        required  = sk.get("required", 7)
        gap_val   = max(0, required - proven)
        bar_w     = int(gap_val / 9 * 100)
        clr       = gap_color(gap_val)
        ev        = sk.get("evidence", "—")
        drift     = proven - claimed
        drift_str = (f'<span style="color:#34d399;">+{drift}</span>' if drift > 0
                     else f'<span style="color:#f87171;">{drift}</span>' if drift < 0
                     else '<span style="color:#4a6280;">±0</span>')
        rows += f"""<tr>
          <td><b style='color:#dde4f0; font-family:Syne,sans-serif;'>{sk['name']}</b></td>
          <td style='text-align:center; color:#4a6280; font-family:Space Mono,monospace;'>{claimed}/10</td>
          <td style='text-align:center; color:#00c896; font-family:Space Mono,monospace; font-weight:700;'>{proven}/10</td>
          <td style='text-align:center; color:#fbbf24; font-family:Space Mono,monospace;'>{required}/10</td>
          <td style='text-align:center; font-family:Space Mono,monospace; font-size:0.8rem;'>{drift_str}</td>
          <td>
            <div class='gap-bar-bg'><div class='gap-bar' style='width:{bar_w}%;background:{clr};'></div></div>
          </td>
          <td style='color:#2a3a52; font-size:0.76rem; max-width:180px;'>{ev}</td>
        </tr>"""

    st.markdown(f"""
    <table class="sp-table">
      <thead><tr>
        <th>Skill</th><th>Claimed</th><th>Proven ★</th><th>Required</th><th>Drift</th><th>Gap</th><th>Interview Evidence</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <div style='font-size:0.68rem; color:#1a2535; margin-top:8px; font-family:Space Mono,monospace;'>★ Proven = score from live interview answers · Drift = Proven minus Claimed</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ROW 3: Charts
    col_bar, col_radar = st.columns([1.4, 1], gap="medium")
    with col_bar:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">Skill Benchmarking — Claimed vs Proven vs Required</div>', unsafe_allow_html=True)
        st.plotly_chart(make_bar_chart(skills), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_radar:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">Competency Radar</div>', unsafe_allow_html=True)
        if skills:
            st.plotly_chart(make_radar(skills), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ROW 4: Interview Prep
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    st.markdown('<div class="sp-section">Interview Preparation - 8 Q&As Based on Your Proven Gaps</div>', unsafe_allow_html=True)
    idata = st.session_state.interview_data or []
    if isinstance(idata, list) and idata:
        for i in range(0, min(len(idata), 8), 2):
            qc = st.columns(2, gap="medium")
            for j, col in enumerate(qc):
                idx = i + j
                if idx < len(idata):
                    item = idata[idx]
                    q_type = re.sub(r"<[^>]+>", "", str(item.get("type", ""))).strip()
                    q_text = re.sub(r"<[^>]+>", "", str(item.get("q", ""))).strip()
                    a_text = re.sub(r"<[^>]+>", "", str(item.get("a", ""))).strip()
                    tip    = re.sub(r"<[^>]+>", "", str(item.get("tip", ""))).strip()
                    tip_html = f'<div class="iq-tip">💡 {tip}</div>' if tip else ""
                    with col:
                        st.markdown(
                            f'<div class="iq-card">'
                            f'<div class="iq-meta">Q{idx+1} · {q_type}</div>'
                            f'<div class="iq-q">{q_text}</div>'
                            f'<div class="iq-alabel">Model Answer</div>'
                            f'<div class="iq-a">{a_text}</div>'
                            f'{tip_html}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
    else:
        st.warning("Interview prep unavailable.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ROW 5: Roadmap + Learning Curve
    col_road, col_curve = st.columns([1.4, 1], gap="medium")

    with col_road:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        # total hours summary
        rdata = st.session_state.roadmap_data or []
        total_hours = sum(d.get("hours", 1.5) for d in rdata[:14])
        st.markdown(f'<div class="sp-section">14-Day Adjacency-Prioritised Roadmap <span style="font-size:0.65rem; color:#2a3a52; font-weight:400; letter-spacing:0;">· {total_hours:.0f} hrs total · ~{total_hours/14:.1f} hrs/day</span></div>', unsafe_allow_html=True)
        type_icons = {"video": "▶", "course": "🎓", "doc": "📖", "book": "📚", "github": "⬡"}
        if isinstance(rdata, list) and rdata:
            for d in rdata[:14]:
                # Strip HTML from all text fields — model sometimes returns HTML tags in JSON strings
                topic    = re.sub(r"<[^>]+>", "", str(d.get("topic", ""))).strip()
                hours    = d.get("hours", 1.5)
                day_num  = d.get("day", "?")
                adj_raw  = re.sub(r"<[^>]+>", "", str(d.get("adjacency_note") or "")).strip()
                adj_html = f'<div style="font-size:0.72rem; color:#00956e; font-style:italic; margin-bottom:3px;">↳ {adj_raw}</div>' if adj_raw and adj_raw.lower() != "null" else ""

                # Strip HTML from each activity
                acts = [re.sub(r"<[^>]+>", "", str(a)).strip() for a in d.get("activities", [])]
                acts_str = " · ".join(acts)

                # Build resource links — strip HTML from labels
                res_parts = []
                for r in d.get("resources", []):
                    label = re.sub(r"<[^>]+>", "", str(r.get("label", "Resource"))).strip()
                    url   = re.sub(r"<[^>]+>", "", str(r.get("url", "#"))).strip()
                    icon  = type_icons.get(r.get("type", ""), "🔗")
                    res_parts.append(f'<a href="{url}" target="_blank">{icon} {label}</a>')
                res_html = "".join(res_parts)

                st.markdown(
                    f'<div class="rm-day">'
                    f'<div class="rm-badge">D{day_num}<br><span style="font-size:0.55rem; color:#006b50;">{hours}h</span></div>'
                    f'<div>'
                    f'{adj_html}'
                    f'<div class="rm-topic">{topic}</div>'
                    f'<div class="rm-act">{acts_str}</div>'
                    f'<div class="rm-res" style="margin-top:6px;">{res_html}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.warning("Roadmap unavailable.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_curve:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown('<div class="sp-section">Projected Readiness Curve</div>', unsafe_allow_html=True)
        st.plotly_chart(make_learning_curve(), use_container_width=True, config={"displayModeBar": False})

        projected = 84
        gain = projected - score
        g_clr = "#34d399" if gain >= 0 else "#f87171"
        st.markdown(f"""
        <div class="proof-compare">
          <div class="proof-box">
            <div class="proof-num" style="color:#34d399;">{projected}%</div>
            <div class="proof-lbl">Day 14 Target</div>
          </div>
          <div class="proof-box">
            <div class="proof-num" style="color:{g_clr};">+{gain}%</div>
            <div class="proof-lbl">Projected Gain</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top:16px;"><div class="sp-section">Quick Wins · 48h</div></div>', unsafe_allow_html=True)
        for d in (rdata or [])[:2]:
            st.markdown(f'<div style="font-size:0.8rem; color:#2a3a52; padding:3px 0; font-family:Space Mono,monospace;">D{d.get("day","?")} → {d.get("topic","")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Restart button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬡  Start New Assessment"):
        for key in ["phase","skill_plan","probe_questions","chat_history",
                    "current_skill_idx","current_q_idx","skill_scores",
                    "final_data","interview_data","roadmap_data",
                    "_jd","_resume"]:
            if key in st.session_state:
                del st.session_state[key]
        # probe_mode intentionally kept so user doesn't re-select every time
        st.rerun()

    # Footer
    st.markdown("""
    <div style='text-align:center; font-family:Space Mono,monospace; font-size:0.58rem; color:#0d1a2a;
                padding:20px; border-top:1px solid rgba(255,255,255,0.03); margin-top:24px; letter-spacing:0.1em;'>
      SKILLPROOF · CATALYST HACKATHON 2025 · DECCAN AI EXPERTS · QWEN · QWEN-PLUS
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  PHASE 0 LANDING (empty state)
# ═══════════════════════════════════════════
if st.session_state.phase == 0 and "sp-shown" not in st.session_state:
    st.markdown("""
    <div style='margin-top:8px; display:flex; gap:14px; flex-wrap:wrap;'>
      <div style='flex:1; min-width:160px; background:#080c18; border:1px solid rgba(0,200,150,0.1); border-radius:10px; padding:18px;'>
        <div style='font-family:Syne,sans-serif; font-size:0.7rem; font-weight:700; color:#00c896; letter-spacing:0.12em; margin-bottom:8px;'>01 · EXTRACT</div>
        <div style='font-size:0.8rem; color:#2a3a52; line-height:1.6;'>Parse JD & resume. Identify 6 critical skills with claimed levels.</div>
      </div>
      <div style='flex:1; min-width:160px; background:#080c18; border:1px solid rgba(0,200,150,0.1); border-radius:10px; padding:18px;'>
        <div style='font-family:Syne,sans-serif; font-size:0.7rem; font-weight:700; color:#00c896; letter-spacing:0.12em; margin-bottom:8px;'>02 · PROBE</div>
        <div style='font-size:0.8rem; color:#2a3a52; line-height:1.6;'>Conduct a live conversational interview — 2 calibrated questions per skill.</div>
      </div>
      <div style='flex:1; min-width:160px; background:#080c18; border:1px solid rgba(0,200,150,0.1); border-radius:10px; padding:18px;'>
        <div style='font-family:Syne,sans-serif; font-size:0.7rem; font-weight:700; color:#00c896; letter-spacing:0.12em; margin-bottom:8px;'>03 · CALIBRATE</div>
        <div style='font-size:0.8rem; color:#2a3a52; line-height:1.6;'>Score each answer in real-time. Interview answers override resume claims.</div>
      </div>
      <div style='flex:1; min-width:160px; background:#080c18; border:1px solid rgba(0,200,150,0.1); border-radius:10px; padding:18px;'>
        <div style='font-family:Syne,sans-serif; font-size:0.7rem; font-weight:700; color:#00c896; letter-spacing:0.12em; margin-bottom:8px;'>04 · REPORT</div>
        <div style='font-size:0.8rem; color:#2a3a52; line-height:1.6;'>Full career intelligence — Proof Score, gap map, roadmap, interview prep.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
