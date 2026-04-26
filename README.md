# ⬡ SkillProof — Prove What You Know

> **Deccan.ai Catalyst Hackathon · April 2026**
> AI-powered skill verification that separates resume claims from real-world competence.

---

## What It Does

SkillProof is a career intelligence tool that conducts a live AI-driven interview, calibrates your actual skill levels against what your resume claims, and delivers a full gap analysis — with a personalised 14-day learning roadmap to close those gaps before your real interview.

**The core insight:** Resumes lie — not because candidates are dishonest, but because self-assessment is hard. SkillProof replaces guesswork with evidence.

---

## How It Works — 4 Phases

```
01 EXTRACT → 02 PROBE → 03 CALIBRATE → 04 REPORT
```

| Phase | What Happens |
|-------|-------------|
| **01 · Extract** | Paste or upload a JD + resume. The AI parses both, identifies the 6 most critical skills, infers claimed levels from the resume, and sets required levels from the JD. |
| **02 · Probe** | A conversational AI interviewer asks 2 calibrated questions per skill — warm and human, not an exam. You answer in a chat interface. |
| **03 · Calibrate** | Each answer is scored 1–10 in real-time. Interview evidence overrides resume claims, computing a "Proof Score". |
| **04 · Report** | Full dashboard: Proof Score gauge, skill gap table with drift analysis, bar + radar charts, 8 interview prep Q&As, and a 14-day adjacency-prioritised learning roadmap. |

---

## Scoring Logic

### Proof Score (0–100)

```
Proof Score = weighted_average(proven_scores) × 10
```

Each skill's **proven score** is determined by the AI evaluator which considers:
- Accuracy and depth of the candidate's answer
- Evidence of practical application vs. theoretical knowledge
- Calibration against the required level for the role

**Drift** = `Proven − Claimed`
- Positive drift → candidate under-sold themselves
- Negative drift → resume may be over-claiming

**Verdicts:**
| Score | Verdict |
|-------|---------|
| < 50 | Needs Development |
| 50–69 | Emerging Candidate |
| 70–84 | Strong Candidate |
| 85–100 | Elite Candidate |

### Gap Priority
Gaps are flagged Critical / High / Medium / Proficient based on the delta between proven level and required level. The roadmap prioritises skills using **adjacency ordering** — skills that unlock other skills come first.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  Phase stepper · Chat UI · Plotly charts · Dashboard    │
└───────────────────┬─────────────────────────────────────┘
                    │ User input (JD, resume, chat answers)
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Prompt Orchestration Layer                  │
│  EXTRACT_SKILLS → BATCH_PROBE → EVALUATE → REPORT GEN   │
└───────────────────┬─────────────────────────────────────┘
                    │ Structured JSON requests
                    ▼
┌─────────────────────────────────────────────────────────┐
│            Qwen / Qwen-Plus via OpenAI-compat API        │
│         (skill extraction · interview · scoring)         │
└─────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  PDF Resume Parser      Session State Store
  (pypdf)                (Streamlit in-memory)
```

All AI calls return structured JSON. The app parses, validates, and renders results in a single-page dashboard.

---

## Sample Input & Output

### Input
**Job Description (excerpt):**
> "We are looking for a Senior Data Scientist with strong experience in Python, machine learning model deployment, SQL, and stakeholder communication…"

**Resume (excerpt):**
> "5 years in data science. Proficient in Python, scikit-learn, TensorFlow. Led 3 ML projects end-to-end…"

### Output — Proof Score Dashboard
```
Proof Score: 67 / 100   →   Emerging Candidate

Skill           Claimed  Proven  Required  Drift
──────────────────────────────────────────────────
Python            8/10    7/10     8/10    -1  ✓
ML Deployment     7/10    5/10     9/10    -2  ⚠ HIGH GAP
SQL               6/10    6/10     7/10    0   ✓
Communication     7/10    8/10     6/10    +1  ✓ (exceeded)
Statistics        5/10    4/10     8/10    -1  ⚠ CRITICAL GAP
Cloud/MLOps       4/10    3/10     8/10    -1  ⚠ CRITICAL GAP

14-Day Roadmap: 42 hrs total · ~3.0 hrs/day
D1 → ML Deployment Fundamentals (adjacency: unlocks Cloud/MLOps)
D2 → Docker + model serving patterns
...
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.32+ |
| AI Model | Qwen-Plus (via OpenAI-compatible endpoint) |
| Charting | Plotly (gauge, bar, radar, learning curve) |
| PDF Parsing | pypdf |
| Fonts | Syne · Space Mono · Instrument Sans |
| Hosting | Streamlit Community Cloud |

---

## Local Setup

### Prerequisites
- Python 3.10+
- A Qwen API key (set via the sidebar in the app, or as an env var)

### Install & Run

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/skillproof
cd skillproof

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run skillproof_app.py
```

### API Key
Enter your **Qwen API key** in the sidebar when the app opens. The key is stored in session state only — never persisted.

> If you're using a different OpenAI-compatible endpoint, update the `base_url` in the sidebar configuration.

---

## Project Structure

```
skillproof/
├── skillproof_app.py      # Main application (single-file)
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── assets/
    └── architecture.png   # Architecture diagram
```

---

## Roadmap (Post-Hackathon)

- [ ] Export PDF report
- [ ] Multi-role comparison mode
- [ ] Recruiter view (bulk candidate scoring)
- [ ] Voice interview mode
- [ ] Integration with LinkedIn profile import

---

## Team

Built for the **Deccan.ai Catalyst Hackathon · April 2026**
Submitted by: **Prakash** · [prakashrajastro@gmail.com](mailto:prakashrajastro@gmail.com)

---

*SkillProof · Catalyst Hackathon 2026 · Deccan AI Experts*
