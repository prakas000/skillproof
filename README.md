# ⬡ SkillProof — Prove What You Know

> AI-powered candidate assessment platform that replaces resume guesswork with live skill verification through a conversational probe interview.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![AI](https://img.shields.io/badge/AI-GPT--4o--mini%20%7C%20Qwen--plus-8A2BE2?style=flat-square)

---

## What It Does

SkillProof takes a job description and a candidate's resume, conducts a live AI-powered probe interview, and produces a calibrated **Proof Score** — the difference between what the resume claims and what the candidate can actually demonstrate.

**Resume claims ≠ proven skills. SkillProof measures both.**

---

## Features

### 🔍 5-Phase Assessment Pipeline
| Phase | Description |
|-------|-------------|
| Resume Parse | Extracts text from PDF or plain-text resume |
| Skill Extraction | LLM identifies up to 6 critical skills from the JD, rates claimed vs required level (1–10) |
| Live Probe Interview | Conversational AI interview — sounds like a real hiring manager, not an exam |
| Calibrated Scoring | Per-skill scores averaged only from answered questions; skipped skills excluded from overall score |
| Career Report | Full dashboard with Proof Score, skill gap table, interview prep, 14-day roadmap |

### ⚡ Three Interview Modes
| Mode | Questions | Depth |
|------|-----------|-------|
| Quick Scan | 6 total (1 per skill) | Beginner |
| Standard | ~12 total (2 per skill) | Mixed |
| Deep Probe | ~18 total (3 per skill) | Advanced |

### 📊 Report Dashboard
- **Proof Score** — gauge chart comparing resume score vs interview-proven score
- **Calibrated Skill Table** — Claimed / Proven / Required / Drift / Gap bar per skill; skipped skills shown as `—` and excluded from scoring
- **Competency Map** — bar chart + radar chart (Claimed vs Proven vs Required)
- **Job Links** — pre-populated search links to LinkedIn, Indeed, Glassdoor, Naukri, Wellfound, Google Jobs
- **Interview Prep** — 6 Q&As (conceptual, technical, behavioural) tailored to the candidate's gaps
- **14-Day Adjacency-Prioritised Roadmap** — ordered by proximity to existing strengths, with real resource links
- **Projected Readiness Curve** — learning trajectory chart
- **Assessment History** — in-session history of all completed assessments

### 🤖 Multi-Provider AI Fallback
Tries providers in order, silently falling back on any error:
1. **OpenAI** `gpt-4o-mini`
2. **DashScope / Qwen** `qwen-plus`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit (wide layout, custom CSS design system) |
| AI | OpenAI-compatible API (`openai` Python SDK) |
| PDF Parsing | `pypdf` |
| Charts | `plotly` (gauge, bar, radar, scatter) |
| Fonts | Syne · Space Mono · Instrument Sans (Google Fonts) |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` for parallel LLM calls |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/skillproof.git
cd skillproof
```

### 2. Install dependencies

```bash
pip install streamlit openai pypdf plotly
```

Or with a requirements file:

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
streamlit>=1.32.0
openai>=1.0.0
pypdf>=4.0.0
plotly>=5.0.0
```

### 3. Set up API keys

#### Local development — `.streamlit/secrets.toml`

Create the file `.streamlit/secrets.toml` in the project root:

```toml
OPENAI_API_KEY = "sk-..."
DASHSCOPE_API_KEY = "sk-..."   # optional — used as fallback
```

At least one key is required. If only one provider is configured, the other is silently skipped.

#### Streamlit Cloud deployment

1. Go to your app in [share.streamlit.io](https://share.streamlit.io)
2. Click **Settings → Secrets**
3. Add the same key-value pairs:
```
OPENAI_API_KEY = "sk-..."
DASHSCOPE_API_KEY = "sk-..."
```

### 4. Run locally

```bash
streamlit run skillproof_app.py
```

---

## Deployment on Streamlit Cloud

1. Push `skillproof_app.py` to a public or private GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, branch, and set the main file to `skillproof_app.py`
4. Add your secrets under **Settings → Secrets**
5. Click **Deploy** — live in ~60 seconds

No Docker, no server config needed.

---

## Project Structure

```
skillproof/
├── skillproof_app.py   # entire application (single file)
├── requirements.txt    # pip dependencies
├── .streamlit/
│   └── secrets.toml    # API keys (local only — never commit this)
└── README.md
```

> SkillProof is intentionally a single-file app. All logic, CSS, prompts, charts, and UI live in `skillproof_app.py` for easy deployment and portability.

---

## How Scoring Works

```
Proof Score = (avg_proven × 0.5) + (domain_fit × 0.3) + (experience_baseline × 0.2)
```

- **avg_proven** — average interview score (1–10) across all answered skills only
- Skipped skills are **excluded** from the average — they show `—` in the table
- Skills never presented in the interview are also treated as unassessed
- Score is clamped between 40–92 to reflect realistic hiring ranges
- **Resume Score** uses claimed levels with the same formula for comparison

### Skill Assessment Logic
Each answered skill gets an independent score:
- Per-question scores accumulate in a temporary buffer (`_current_skill_q_scores`)
- Buffer is averaged when all questions for that skill are complete
- Buffer resets for the next skill
- Skipping a skill (or any question within it) marks the whole skill as not assessed

---

## Environment Variables / Secrets Reference

| Secret Key | Required | Description |
|------------|----------|-------------|
| `OPENAI_API_KEY` | One of these two is required | OpenAI API key — uses `gpt-4o-mini` |
| `DASHSCOPE_API_KEY` | One of these two is required | Alibaba DashScope key — uses `qwen-plus` |

---

## Known Limitations

- **PDF scan/image support**: Scanned (image-only) PDFs cannot be parsed — the resume must contain selectable text
- **Session state**: Assessment history is in-memory per session and resets on browser refresh
- **Roadmap links**: Resource URLs are AI-generated and may occasionally point to non-existent pages — always verify before following
- **Token limits**: Roadmap generation uses up to 8,000 tokens; very slow connections may time out at the 90-second limit

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with Streamlit · Powered by OpenAI & Qwen · Designed for hiring clarity</sub>
</div>
