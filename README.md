# 🧫 PhD Cold Email Generator

A RAG-powered Streamlit app that generates highly targeted, human-sounding cold emails for PhD applications in gut microbiome research.

Built with **Claude Sonnet** (Anthropic API).

---

## ✨ Features

- **Auto-Discover Angles** — paste a research paper and the tool extracts 2–3 specific research gaps/mechanisms to build the email around
- **Manual Focus** — specify your own finding, metabolite, microbe, pathway, and research question
- **Scientific depth enforcement** — every email must include ≥1 metabolite, ≥1 microbe, ≥1 pathway/gene, ≥1 technique
- **Self-scoring loop** — Claude scores the email on depth, tone, specificity, and originality before outputting
- **Human tone rules** — no "cutting-edge", no "passionate", no robotic phrasing
- **Editable output** — edit the email directly in the app and download as .txt

---

## 🚀 Deploying to Streamlit Cloud

### 1. Push this repo to GitHub

```bash
git init
git add .
git commit -m "Initial commit — PhD Cold Email Generator"
git branch -M main
git remote add origin https://github.com/sdazz56/phd-cold-email-generator.git
git push -u origin main
```

### 2. Create the app on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your repo: `sdazz56/phd-cold-email-generator`
4. Branch: `main`
5. Main file path: `app.py`
6. Click **Deploy**

### 3. Add your API key (Secrets)

In Streamlit Cloud, after deployment:

1. Open your app → **⋮ menu** → **Settings** → **Secrets**
2. Add:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

3. Save — the app will restart automatically.

---

## 🗂 Project Structure

```
phd-cold-email-generator/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Theme and server config
└── README.md
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (get one at console.anthropic.com) |

---

## 📋 How to Use

1. **Paste the research paper** (abstract + methods + results)
2. **Choose your focus** — auto-discover angles or specify your own
3. **Add your CV** highlights
4. **Set the professor** and degree settings
5. **Generate** — review scores and refine if needed

---

## ⚠️ Notes

- Always verify scientific details (metabolites, genes, pathways) against the actual paper before sending
- Small personal edits to the generated email always improve authenticity
- The app uses `claude-sonnet-4-5` — ensure your API key has access

---

*Inspired by [arpon-kapuria/cold-mail-generator](https://github.com/arpon-kapuria/cold-mail-generator)*
