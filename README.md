# SkillProof - Prove What You Know

> **An AI agent that conversationally assesses real skill proficiency - not just resume claims.**

![SkillProof](https://img.shields.io/badge/SkillProof-Catalyst%202025-00c896?style=for-the-badge)
![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq%20%2B%20Llama--3.3--70B-orange?style=for-the-badge)
![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=for-the-badge)

---

## The Problem

Every resume-screening tool today does the same thing: compare keywords in a resume against keywords in a job description. A candidate who writes "proficient in PyTorch" scores identically to one with 3 years of production ML experience. **There is no signal separation.**

Recruiters waste hours on interviews that reveal the resume was inflated. Candidates who are genuinely strong but wrote a weak resume get filtered out. The screening layer is broken.

---

## What SkillProof Does

SkillProof is a conversational AI agent that **probes each claimed skill with targeted questions** and scores the candidate's live answers - not their resume text.

The final **Proof Score** is calibrated from interview performance, not document parsing. Resume claims are shown alongside proven scores so the drift is visible and actionable.

### The Core Insight

> A resume is a marketing document. An interview answer is evidence.  
> SkillProof treats them accordingly - interview answers override resume claims in scoring.

---

## Architecture & Key Decisions

### Pipeline (4 Phases)

```
Phase 1 - EXTRACT
  └── Parse JD + Resume
  └── Identify 6 critical skills with claimed level (from resume) 
      and required level (from JD)
  └── Assign probe depth per skill: beginner | intermediate | advanced

Phase 2 - PROBE  (the core differentiator)
  └── For each skill → generate N calibrated questions (user-selectable)
  └── Q1: Conceptual - tests foundational understanding
  └── Q2: Practical  - tests real-world application ability
  └── Each answer evaluated in real-time by the model
  └── Scoring rubric: accuracy, technical vocabulary, hands-on evidence, edge-case handling
  └── Live calibration panel updates as candidate answers

Phase 3 - CALIBRATE
  └── Final scoring call receives: resume text + full interview transcript
  └── Interview answers explicitly weighted over resume claims (50% vs 40% vs 10% rubric)
  └── Shows "Drift" column: Proven score minus Claimed score per skill

Phase 4 - REPORT
  └── Proof Score (interview-calibrated)
  └── Resume-only score (for comparison)
  └── Skill gap table with evidence from actual answers
  └── Bar chart: Resume Claim vs Proven vs Required (3-way comparison)
  └── Radar chart, 14-day learning roadmap, 8 interview prep Q&As
  └── Live job search links for the identified role
```

### Key Architectural Decisions

**1. Upfront question generation, not on-the-fly**  
All probe questions for all skills are generated before the interview starts. This avoids latency mid-conversation and allows consistent depth calibration. Trade-off: slightly longer loading at the start, but a smoother interview experience.

**2. Hardened JSON-only API contract**  
Every Groq call uses a strict system prompt forcing pure JSON output. A 5-strategy fallback parser (`parse_json()`) handles edge cases: direct parse → clean fences → extract `{...}` block → extract `[...]` block → wrap bare content. This makes the pipeline robust against model formatting drift.

**3. Temperature = 0.0 for scoring calls**  
Deterministic output for evaluation and scoring. Slight temperature (0.1) only for question generation to avoid repetitive phrasing.

**4. Interview transcript as ground truth**  
The final `FINAL_ANALYSIS_PROMPT` explicitly instructs the model: *"If a candidate claimed X on their resume but demonstrated Y in the interview, use Y."* The transcript is passed alongside the resume so both are visible to the scoring model.

**5. Session-cached results**  
Results are fingerprinted (MD5 of JD + resume text) and cached in `st.session_state`. Re-running with the same inputs shows cached results instantly - no redundant API calls.

**6. User-selectable probe depth**  
Three modes give the user control over assessment length:
- ⚡ Quick Scan - 1 question/skill (~6 total)
- ⬡ Standard - 2 questions/skill (~12 total)  
- 🔬 Deep Probe - 3 questions/skill (~18 total)

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| LLM Inference | Groq + Llama-3.3-70B-Versatile | Sub-second latency for conversational feel; best instruction-following at this speed |
| Frontend | Streamlit | Rapid iteration; chat + charts + state in one framework |
| PDF Parsing | pypdf | Lightweight, no external dependencies |
| Charts | Plotly | Interactive; supports gauge, radar, bar, and scatter in one lib |
| Scoring Model | WSS v4 (Weighted Semantic Scoring) | Custom rubric weighting interview evidence > resume claims |

---

## Setup & Running Locally

### Prerequisites
- Python 3.8+
- A free [Groq API key](https://console.groq.com)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/skillproof.git
cd skillproof
pip install -r requirements.txt
```

### Run

```bash
streamlit run skillproof_app.py
```

Enter your Groq API key in the sidebar when the app opens.

### Optional: Pre-configure your API key locally

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

The app reads this automatically - leave the sidebar field blank.

---

## Live Demo

🔗 **[skillproof.streamlit.app](https://YOUR_APP_URL.streamlit.app)**  
*(No setup needed - API key pre-configured for demo)*

---

## Submission - Catalyst 2025

**Built by:** Prakash Raj Govindaraj
**Hackathon:** Catalyst by deccan.ai - April 24–27, 2025  
**Track:** AI Agent  
**Stack:** Groq · Llama-3.3-70B · Streamlit · Python  

---

## What Makes This Production-Minded

- **Error handling at every layer** - try/except around all API calls, JSON parsing fallbacks, graceful degradation if interview/roadmap generation fails
- **No hardcoded secrets** - API key via Streamlit secrets or user input; never in code
- **Input sanitization** - HTML stripped from model responses before rendering to prevent injection via chat bubbles
- **Stateful session management** - phase tracking, answer history, and calibration scores persist correctly across rerenders
- **Modular prompts** - each pipeline stage is a separate, testable prompt constant; easy to swap models or adjust rubrics
