# 🧫 PhD Cold Email Generator

A RAG-powered Streamlit app that generates highly targeted, human-sounding cold emails for PhD applications in gut microbiome research.

Now featuring **Multi-LLM support** (Gemini, OpenAI, Anthropic) via a unified **LiteLLM** backend.

---

## ✨ Features

- **Multi-LLM Support** — Unified backend supporting Gemini, OpenAI, Claude, and more.
- **Provider Tabs** — Modernized Step 0 UI for seamless provider and model switching.
- **Auto-Discover Angles** — Paste a research paper and the tool extracts 2–3 specific research gaps/mechanisms.
- **Scientific Depth Enforcement** — Every email must include ≥1 metabolite, ≥1 microbe, ≥1 pathway/gene, ≥1 technique.
- **Self-Scoring Loop** — The AI scores the email on depth, tone, specificity, and originality before outputting.
- **Human Tone Rules** — No robotic phrasing ("cutting-edge", "passionate", "pleased to meet you").

---

## 🚀 Getting Started

### 1. Installation

```bash
# Clone the repo
git clone https://github.com/sdazz56/PhD-Cold-Email-Generator.git
cd PhD-Cold-Email-Generator

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Locally

```bash
streamlit run app.py
```

---

## 🗂 Project Structure

```
phd-cold-email-generator/
├── app.py                  # Main Entry Point
├── src/                    # Logic Layer
│   ├── llm.py              # Unified LiteLLM Backend
│   ├── utils.py            # Helpers & Data Processing
│   ├── prompts.py          # RAG & Generation Prompts
│   └── styles.py           # Custom CSS & Theming
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🔑 AI Models supported

| Provider | Supported Models |
|---|---|
| **Gemini** | 1.5 Pro, 1.5 Flash, 3.1 Pro (Preview) |
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-5.4 (Preview) |
| **Anthropic** | Claude 3.5 Sonnet, Claude 4 (Preview) |
| **Deepseek** | Deepseek V3 |

*Note: Futuristic models (GPT-5, Gemini 3, etc.) are intelligently mapped to the best current versions via LiteLLM.*

---

## 📋 How to Use

1. **Step 0: API Setup** — Select your provider, model, and enter your API key.
2. **Step 1: Research Paper** — Paste the abstract + methods + results.
3. **Step 2: Focus / Angle** — Auto-discover or specify manual scientific targets.
4. **Step 3: Your Profile** — Add your degree and research highlights.
5. **Step 4: Target Lab** — Enter the professor's name and lab focus.
6. **Step 5: Generate** — Review, edit, and download your email.

---

## ⚠️ Scientific Integrity

- Always verify scientific details (metabolites, genes, pathways) against the actual paper.
- The tool identifies **gaps**, but your personal background makes the email truly unique.

---

*Inspired by [arpon-kapuria/cold-mail-generator](https://github.com/arpon-kapuria/cold-mail-generator)*
