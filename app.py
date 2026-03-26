import streamlit as st
import anthropic
import google.generativeai as genai
import litellm
import json
import re

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhD Cold Email Generator",
    page_icon="🧫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1a1916 !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(255,255,255,0.55) !important;
    font-size: 12px !important;
}

/* Main background */
.stApp { background: #f6f4ef; }

/* Headers */
h1, h2, h3 {
    font-family: 'Instrument Serif', serif !important;
    font-weight: 400 !important;
}

/* Step header */
.step-header {
    background: white;
    border: 1px solid #ddd8cc;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(26,25,22,0.06);
}
.step-eyebrow {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #2d6a4f;
    margin-bottom: 4px;
}
.step-title {
    font-family: 'Instrument Serif', serif;
    font-size: 28px;
    color: #1a1916;
    margin: 0;
    line-height: 1.15;
}
.step-title em { color: #2d6a4f; font-style: italic; }
.step-desc { color: #706a5c; font-size: 14px; margin-top: 6px; font-weight: 300; }

/* Cards */
.info-card {
    background: white;
    border: 1px solid #ddd8cc;
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(26,25,22,0.05);
}

/* Callouts */
.callout-green {
    background: rgba(45,106,79,0.06);
    border: 1px solid rgba(45,106,79,0.2);
    border-left: 3px solid #2d6a4f;
    border-radius: 7px;
    padding: 11px 14px;
    font-size: 13px;
    color: #706a5c;
    margin: 12px 0;
    line-height: 1.55;
}
.callout-amber {
    background: #fef3c7;
    border: 1px solid rgba(154,107,0,0.25);
    border-left: 3px solid #9a6b00;
    border-radius: 7px;
    padding: 11px 14px;
    font-size: 13px;
    color: #78510a;
    margin: 12px 0;
}

/* Angle cards */
.angle-card {
    background: white;
    border: 2px solid #ddd8cc;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.angle-card.selected {
    border-color: #2d6a4f;
    background: rgba(45,106,79,0.02);
}
.angle-headline { font-weight: 600; font-size: 15px; color: #1a1916; margin-bottom: 6px; }
.angle-body { font-size: 13px; color: #706a5c; line-height: 1.6; margin-bottom: 10px; }
.angle-question { font-size: 13px; color: #1a1916; font-style: italic; margin-bottom: 10px; }
.tag {
    display: inline-block;
    font-size: 11px;
    padding: 3px 9px;
    border-radius: 4px;
    margin-right: 6px;
    font-weight: 500;
}
.tag-metabolite { background: #fef3c7; color: #9a6b00; border: 1px solid rgba(154,107,0,0.3); }
.tag-microbe { background: #d8f3dc; color: #2d6a4f; border: 1px solid rgba(45,106,79,0.3); }
.tag-pathway { background: #fde8e8; color: #9b2226; border: 1px solid rgba(155,34,38,0.3); }

/* Score badges */
.scores-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.score-badge {
    background: white;
    border: 1px solid #ddd8cc;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: center;
    min-width: 90px;
}
.score-val { font-size: 22px; font-weight: 600; color: #2d6a4f; font-family: monospace; }
.score-lbl { font-size: 10px; color: #706a5c; text-transform: uppercase; letter-spacing: 0.07em; }

/* Email output */
.email-output {
    background: white;
    border: 1px solid #ddd8cc;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(26,25,22,0.08);
}
.email-bar {
    background: #1a1916;
    padding: 14px 22px;
    color: rgba(255,255,255,0.9);
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-size: 15px;
}
.email-body {
    padding: 28px 32px;
    font-size: 14px;
    line-height: 1.9;
    color: #1a1916;
    font-weight: 300;
    white-space: pre-wrap;
    word-break: break-word;
}
.email-footer {
    background: #f0ede6;
    border-top: 1px solid #ddd8cc;
    padding: 12px 22px;
    font-size: 12px;
    color: #706a5c;
}

/* Progress steps in sidebar */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    opacity: 0.45;
}
.nav-item.active { opacity: 1; }
.nav-item.done { opacity: 0.7; }
.nav-bullet {
    width: 24px; height: 24px;
    border-radius: 50%;
    border: 1.5px solid rgba(255,255,255,0.25);
    color: rgba(255,255,255,0.5);
    font-size: 11px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-family: monospace;
}
.nav-item.active .nav-bullet {
    border-color: #52b788;
    color: #52b788;
}
.nav-item.done .nav-bullet {
    background: #52b788;
    border-color: #52b788;
    color: #1a1916;
}
.nav-label { font-size: 12px; font-weight: 500; }
.nav-sub { font-size: 10px; color: rgba(255,255,255,0.35) !important; }

/* Streamlit overrides */
.stTextInput > label, .stTextArea > label, .stSelectbox > label {
    font-size: 11.5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #706a5c !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #f6f4ef !important;
    border: 1.5px solid #ddd8cc !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #2d6a4f !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.1) !important;
}
.stButton > button {
    background: #1a1916 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #2d6a4f !important;
    transform: translateY(-1px) !important;
}
.stRadio > label {
    font-size: 11.5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #706a5c !important;
}
div[data-testid="stHorizontalBlock"] { gap: 16px; }
</style>
""", unsafe_allow_html=True)

# ─── Session state init ────────────────────────────────────────────────────────
defaults = {
    "step": 0,
    "api_model": "anthropic/claude-3-5-sonnet-20240620",
    "api_key": "",
    "paper_title": "",
    "paper_authors": "",
    "paper_text": "",
    "focus_mode": "Auto-Discover",
    "angles": [],
    "selected_angle_idx": 0,
    "final_focus": None,
    "manual_focus": {},
    "cv_brief": "",
    "user_name": "",
    "user_email": "",
    "user_degree": "",
    "user_institute": "",
    "user_country": "",
    "user_cv": "",
    "prof_name": "",
    "prof_univ": "",
    "prof_lab": "",
    "prof_focus": "",
    "degree_seeking": "PhD",
    "start_date": "",
    "generated_email": "",
    "scores": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_llm(model_name, api_key):
    """Get LLM client based on model and key."""
    if model_name.startswith("anthropic/"):
        try:
            return anthropic.Anthropic(api_key=api_key)
        except:
            st.error("❌ Invalid Anthropic API key.")
            st.stop()
    elif model_name.startswith("gemini/"):
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(model_name.split("/")[-1])
        except:
            st.error("❌ Invalid Gemini API key.")
            st.stop()
    else:  # LiteLLM for Kimi, Deepseek, Qwen
        litellm.api_key = api_key
        litellm.model_mapping = {
            "kimi/moonshot": "moonshot-v1-8k",
            "deepseek/deepseek-chat": "deepseek/deepseek-chat",
            "qwen/qwen2.5": "qwen/Qwen2.5-7B-Instruct",
        }
        return model_name

def call_llm(prompt: str, max_tokens: int = 1500) -> str:
    model_name = st.session_state.api_model
    api_key = st.session_state.api_key
    if not api_key:
        st.error("❌ Please set your API key in Step 0.")
        st.stop()
    
    llm = get_llm(model_name, api_key)
    
    if model_name.startswith("anthropic/"):
        client = llm
        msg = client.messages.create(
            model=model_name.split("/")[-1],
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    elif model_name.startswith("gemini/"):
        response = llm.generate_content(prompt, generation_config={"max_output_tokens": max_tokens})
        return response.text
    else:
        # LiteLLM
        response = litellm.completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

def go_to(step: int):
    st.session_state.step = step

def parse_scores(raw: str) -> dict:
    m = re.search(
        r"SCORES:\s*depth=(\d+)/10,\s*tone=(\d+)/10,\s*specificity=(\d+)/10,\s*originality=(\d+)/10",
        raw, re.IGNORECASE
    )
    if m:
        return {
            "Paper Depth": int(m.group(1)),
            "Human Tone":  int(m.group(2)),
            "Specificity": int(m.group(3)),
            "Originality": int(m.group(4)),
        }
    return {}

def extract_email(raw: str) -> str:
    if "---EMAIL---" in raw:
        return raw.split("---EMAIL---", 1)[1].strip()
    # Fallback: strip score line
    return re.sub(r"SCORES:.*\n?", "", raw, flags=re.IGNORECASE).strip()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧫 PhD Cold Email Generator")
    st.markdown("*Multi-LLM Support · Microbiome · Germany*")
    st.divider()

    # Main steps navigation (shifted by 1)
    steps_info = [
        ("Research Paper",      "Most critical input"),
        ("Focus / Angle",       "Gap or auto-discover"),
        ("Your CV & Profile",   "Skills · experience"),
        ("Professor + Settings","Target lab · degree"),
        ("Generated Email",     "Review & send"),
    ]
    for i, (label, sub) in enumerate(steps_info, 1):
        current = st.session_state.step
        step_num = i + 1
        status = "active" if current == step_num else ("done" if current > step_num else "")
        bullet = "✓" if current > step_num else str(step_num)
        st.markdown(f"""
        <div class="nav-item {status}">
            <div class="nav-bullet">{bullet}</div>
            <div>
                <div class="nav-label">{label}</div>
                <div class="nav-sub">{sub}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1);
         border-radius:8px; padding:12px 14px; font-size:12px; color:rgba(255,255,255,0.45); line-height:1.55;">
    <strong style="color:#52b788;">Using:</strong> {st.session_state.api_model.split('/')[0].title()}
    </div>""", unsafe_allow_html=True)

    if st.session_state.step > 1:
        st.divider()
        if st.button("🔄 Start Over", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

# ─── STEP 0: API Setup ────────────────────────────────────────────────────────
if st.session_state.step == 0:
    st.markdown("""
    <div class="step-header">
        <div class="step-eyebrow">Step 00 — API Setup</div>
        <div class="step-title">Choose Your <em>AI Model</em> & Key</div>
        <div class="step-desc">Enter your API key to unlock generation. Keys persist during session.</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.api_model = st.selectbox(
            "AI Model",
            [
                "anthropic/claude-3-5-sonnet-20240620",
                "gemini/gemini-1.5-pro-latest",
                "gemini/gemini-1.5-flash-latest",
                "kimi/moonshot-v1-8k",
                "deepseek/deepseek-chat",
                "qwen/qwen2.5",
            ],
            index=0,
        )
    with col2:
        st.session_state.api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            help="Get from: Anthropic, Google AI Studio, Kimi.ai, Deepseek, Alibaba Qwen",
        )

    st.markdown("""
    <div class="callout-green">
    🔑 <strong>Quick Setup:</strong><br>
    • Anthropic: console.anthropic.com<br>
    • Gemini: aistudio.google.com/app/apikey<br>
    • Kimi/Deepseek/Qwen: platform.kimi.ai / platform.deepseek.com / dashscope.aliyun.com
    </div>""", unsafe_allow_html=True)

    if st.button("✅ API Ready — Start!", type="primary"):
        if st.session_state.api_key.strip():
            st.session_state.step = 1
            st.success("API configured!")
            st.rerun()
        else:
            st.error("⚠️ Enter your API key.")

# ─── STEP 1: Paper ────────────────────────────────────────────────────────────
if st.session_state.step == 1:
    st.markdown("""
    <div class="step-header">
        <div class="step-eyebrow">Step 01 — Most Critical Input</div>
        <div class="step-title">The Research <em>Paper</em></div>
        <div class="step-desc">Paste the full paper, abstract + methods + results, or a detailed summary.
        Everything else is built around this.</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.session_state.paper_title = st.text_input(
            "Paper Title",
            value=st.session_state.paper_title,
            placeholder="e.g. Gut microbiota-derived butyrate regulates intestinal barrier function via HIF-1α"
        )
        st.session_state.paper_authors = st.text_input(
            "Authors & Journal (optional)",
            value=st.session_state.paper_authors,
            placeholder="e.g. Smith et al., Nature Microbiology 2024"
        )
        st.session_state.paper_text = st.text_area(
            "Full Text / Abstract + Key Findings",
            value=st.session_state.paper_text,
            height=320,
            placeholder=(
                "Paste the paper content here — the more detail the better.\n\n"
                "At minimum include:\n"
                "• Abstract\n"
                "• Key methods (e.g. metabolomics, 16S rRNA, cohort design)\n"
                "• Main findings (exact metabolites, microbial species, pathways)\n"
                "• What remains unclear or future directions\n\n"
                "The tool extracts specific mechanisms, not just the topic."
            )
        )

    with col2:
        st.markdown("""
        <div class="callout-green">
        💡 <strong>More detail = better email.</strong><br><br>
        Include exact metabolite names, microbial genus/species, gene names, and statistical findings.
        Vague input produces vague emails.
        </div>
        <div class="callout-amber" style="margin-top:12px;">
        ⚠️ <strong>What to paste:</strong><br><br>
        Abstract + Methods summary + Results (especially specific metabolites, species, and effect sizes)
        + Discussion / future directions.
        </div>
        <div style="background:white; border:1px solid #ddd8cc; border-radius:10px; padding:16px 18px; margin-top:12px;">
        <div style="font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#2d6a4f; margin-bottom:10px;">
        Scientific elements extracted
        </div>
        <div style="font-size:12.5px; color:#706a5c; line-height:1.8;">
        🧪 Specific metabolites<br>
        🦠 Microbial genus / species<br>
        🔬 Pathways & genes<br>
        📊 Methods & techniques<br>
        ❓ Research gaps<br>
        💡 Possible research directions
        </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    if st.button("Continue to Focus Selection →", type="primary"):
        if not st.session_state.paper_title.strip():
            st.error("⚠ Please enter the paper title.")
        elif len(st.session_state.paper_text.strip()) < 100:
            st.error("⚠ Please paste more paper content — at least the abstract and key findings.")
        else:
            go_to(2)
            st.rerun()

# ─── STEP 2: Focus ────────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    st.markdown("""
    <div class="step-header">
        <div class="step-eyebrow">Step 02 — Research Angle</div>
        <div class="step-title">Choose Your <em>Focus</em></div>
        <div class="step-desc">Specify your angle — or let the tool analyse the paper and surface the best gaps for you.</div>
    </div>""", unsafe_allow_html=True)

    mode = st.radio(
        "Focus Mode",
        ["🔍  Auto-Discover Angles", "✍️  I Have a Specific Angle"],
        horizontal=True,
        index=0 if st.session_state.focus_mode == "Auto-Discover" else 1
    )
    st.session_state.focus_mode = "Auto-Discover" if "Auto" in mode else "Manual"
    st.divider()

    # ── AUTO MODE ──
    if st.session_state.focus_mode == "Auto-Discover":
        st.markdown("""
        <div class="callout-green">
        🔍 The tool will analyse the paper, extract 2–3 specific research gaps or mechanisms,
        and present them as selectable angles. Pick the one that fits your background best.
        </div>""", unsafe_allow_html=True)

        st.session_state.cv_brief = st.text_area(
            "Brief CV Summary (for angle matching — optional)",
            value=st.session_state.cv_brief,
            height=100,
            placeholder="e.g. MSc Microbiology, probiotic R&D (2 yrs), RT-PCR, HPLC, anaerobic fermentation, gut-host interaction models..."
        )

        col_a, col_b = st.columns([2, 3])
        with col_a:
            if st.button("🔬 Analyse Paper & Discover Angles", type="primary"):
                with st.spinner("Analysing paper — extracting mechanisms and gaps..."):
                    prompt = f"""You are an expert microbiome researcher. Carefully read this research paper and extract 3 distinct, highly specific research angles that a PhD applicant could use as the focus of a cold email.

PAPER TITLE: {st.session_state.paper_title}
{f"AUTHORS/JOURNAL: {st.session_state.paper_authors}" if st.session_state.paper_authors else ""}

PAPER CONTENT:
{st.session_state.paper_text}

{f"APPLICANT CV (for relevance ranking):{chr(10)}{st.session_state.cv_brief}" if st.session_state.cv_brief else ""}

For each angle extract:
1. A short compelling headline (max 12 words)
2. A 2-3 sentence description of the specific insight or gap
3. The key metabolite(s) involved
4. The key microbial genus/species
5. The relevant pathway or gene
6. Why this is still unclear (the gap)
7. A precise research question (1 sentence, must include metabolite + microbe + pathway/gene)

Return ONLY valid JSON — no preamble, no markdown fences:
{{
  "angles": [
    {{
      "headline": "...",
      "description": "...",
      "metabolite": "...",
      "microbe": "...",
      "pathway": "...",
      "gap": "...",
      "question": "..."
    }}
  ]
}}"""
                    try:
                        raw = call_llm(prompt, max_tokens=1200)
                        clean = raw.replace("```json", "").replace("```", "").strip()
                        parsed = json.loads(clean)
                        st.session_state.angles = parsed.get("angles", [])
                        st.session_state.selected_angle_idx = 0
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}. Try adding more paper content.")

        # Show angles
        if st.session_state.angles:
            st.markdown("#### Select a Research Angle")
            st.markdown("*Pick the angle you want to build the email around.*")

            for i, a in enumerate(st.session_state.angles):
                selected = i == st.session_state.selected_angle_idx
                card_class = "angle-card selected" if selected else "angle-card"

                st.markdown(f"""
                <div class="{card_class}">
                    <div style="font-size:10px; font-weight:600; letter-spacing:0.12em;
                         text-transform:uppercase; color:#2d6a4f; margin-bottom:6px;">
                        Angle {i+1}
                    </div>
                    <div class="angle-headline">{a['headline']}</div>
                    <div class="angle-body">{a['description']}</div>
                    <div style="font-size:12px; color:#706a5c; margin-bottom:6px;">
                        <strong style="color:#1a1916;">Gap:</strong> {a['gap']}
                    </div>
                    <div class="angle-question">❓ {a['question']}</div>
                    <span class="tag tag-metabolite">⚗ {a['metabolite']}</span>
                    <span class="tag tag-microbe">🦠 {a['microbe']}</span>
                    <span class="tag tag-pathway">🔬 {a['pathway']}</span>
                </div>""", unsafe_allow_html=True)

                if not selected:
                    if st.button(f"Select Angle {i+1}", key=f"sel_{i}"):
                        st.session_state.selected_angle_idx = i
                        st.rerun()
                else:
                    st.markdown(
                        "<div style='font-size:12px; color:#2d6a4f; font-weight:600;"
                        "padding:4px 0 8px;'>✓ Selected</div>",
                        unsafe_allow_html=True
                    )

            st.divider()
            col1, col2 = st.columns([2, 3])
            with col1:
                if st.button("Use Selected Angle →", type="primary"):
                    a = st.session_state.angles[st.session_state.selected_angle_idx]
                    st.session_state.final_focus = {"type": "auto", **a}
                    go_to(3)
                    st.rerun()
            with col2:
                if st.button("← Back to Paper"):
                    go_to(1)
                    st.rerun()
        else:
            if st.button("← Back to Paper"):
                go_to(1)
                st.rerun()

    # ── MANUAL MODE ──
    else:
        st.markdown("""
        <div class="callout-green">
        ✍️ You already know which finding, gap, or mechanism you want to build the email around.
        Describe it in as much scientific detail as possible.
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            manual_focus = st.text_area(
                "What specific finding, mechanism or gap are you focusing on?",
                height=120,
                placeholder=(
                    "e.g. The paper showed that butyrate produced by Faecalibacterium prausnitzii "
                    "activates GPR109A to suppress NF-κB. I want to explore whether this extends "
                    "to SCFA cross-talk with the TLR4 pathway in IBD patients, which wasn't addressed."
                )
            )
            metabolite = st.text_input("Key Metabolite(s)", placeholder="e.g. butyrate, propionate")
            microbe    = st.text_input("Key Microbe(s)", placeholder="e.g. Faecalibacterium prausnitzii")

        with col2:
            pathway   = st.text_input("Pathway / Gene", placeholder="e.g. GPR109A / NF-κB / HIF-1α")
            technique = st.text_input("Your Proposed Technique", placeholder="e.g. LC-MS, anaerobic fermentation")
            question  = st.text_area(
                "Research Question to Pose",
                height=120,
                placeholder=(
                    "e.g. Does butyrate-mediated GPR109A activation modulate TLR4 signalling "
                    "in inflamed colonic epithelium, and can this be recapitulated in anaerobic co-culture models?"
                )
            )

        st.divider()
        col_a, col_b = st.columns([2, 3])
        with col_a:
            if st.button("Use This Focus →", type="primary"):
                if not manual_focus.strip():
                    st.error("⚠ Please describe your specific focus.")
                else:
                    st.session_state.final_focus = {
                        "type": "manual",
                        "description": manual_focus,
                        "metabolite": metabolite,
                        "microbe": microbe,
                        "pathway": pathway,
                        "technique": technique,
                        "question": question,
                    }
                    go_to(3)
                    st.rerun()
        with col_b:
            if st.button("← Back to Paper"):
                go_to(1)
                st.rerun()

# ─── STEP 3: Profile ──────────────────────────────────────────────────────────
elif st.session_state.step == 3:
    st.markdown("""
    <div class="step-header">
        <div class="step-eyebrow">Step 03 — Your Background</div>
        <div class="step-title">CV & <em>Experience</em></div>
        <div class="step-desc">Your skills and experience will be directly connected to the research
        angle — not listed generically.</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.user_name      = st.text_input("Full Name *", value=st.session_state.user_name, placeholder="Your full name")
        st.session_state.user_degree    = st.text_input("Completed Degree *", value=st.session_state.user_degree, placeholder="MSc Microbiology")
        st.session_state.user_country   = st.text_input("Country / Nationality", value=st.session_state.user_country, placeholder="Austria")
    with col2:
        st.session_state.user_email     = st.text_input("Email Address", value=st.session_state.user_email, placeholder="you@university.edu")
        st.session_state.user_institute = st.text_input("Institute & Year *", value=st.session_state.user_institute, placeholder="University of Vienna, 2024")

    st.session_state.user_cv = st.text_area(
        "CV — Paste Key Points *",
        value=st.session_state.user_cv,
        height=260,
        placeholder=(
            "Paste your most relevant experience, projects, and skills here.\n\n"
            "Example:\n\n"
            "Experience:\n"
            "- Probiotic R&D, BioCompany GmbH (2022–2024): strain characterisation,\n"
            "  fermentation optimisation, microbiome-host interaction assays\n"
            "- MSc Thesis: Lactobacillus reuteri adhesion and TLR2 modulation in Caco-2 cells\n\n"
            "Lab Skills: RT-PCR, HPLC, LC-MS (basic), anaerobic fermentation,\n"
            "flow cytometry, ELISA, 16S amplicon sequencing\n\n"
            "Publications / Presentations: [list if any]"
        )
    )

    st.markdown("""
    <div class="callout-green">
    🔗 The email will <strong>directly connect</strong> your specific experience to the chosen
    research angle — not just list your skills generically.
    </div>""", unsafe_allow_html=True)

    st.divider()
    col_a, col_b = st.columns([2, 3])
    with col_a:
        if st.button("Continue →", type="primary"):
            if not st.session_state.user_name.strip():
                st.error("⚠ Please enter your name.")
            elif not st.session_state.user_degree.strip():
                st.error("⚠ Please enter your completed degree.")
            elif not st.session_state.user_institute.strip():
                st.error("⚠ Please enter your institute and year.")
            elif not st.session_state.user_cv.strip():
                st.error("⚠ Please add your CV highlights.")
            else:
                go_to(4)
                st.rerun()
    with col_b:
        if st.button("← Back"):
            go_to(2)
            st.rerun()

# ─── STEP 4: Settings ─────────────────────────────────────────────────────────
elif st.session_state.step == 4:
    st.markdown("""
    <div class="step-header">
        <div class="step-eyebrow">Step 04 — Target & Settings</div>
        <div class="step-title">Professor & <em>Email Settings</em></div>
        <div class="step-desc">Final details about the professor and how the email should be framed.</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.prof_name  = st.text_input("Professor's Name *", value=st.session_state.prof_name, placeholder="Prof. Dr. Maria Müller")
        st.session_state.prof_lab   = st.text_input("Lab / Department (optional)", value=st.session_state.prof_lab, placeholder="Mucosal Immunology Lab / Dept. Gastroenterology")
    with col2:
        st.session_state.prof_univ  = st.text_input("University / Institute", value=st.session_state.prof_univ, placeholder="Charité – Berlin / LMU Munich")
        st.session_state.start_date = st.text_input("Intended Start / Session (optional)", value=st.session_state.start_date, placeholder="Winter Semester 2025 / Spring 2026")

    st.session_state.prof_focus = st.text_area(
        "Lab's Broader Research Focus (optional — helps personalise)",
        value=st.session_state.prof_focus,
        height=80,
        placeholder="e.g. Gut microbiome-immune crosstalk, IBD mechanisms, metabolomics, epithelial barrier function..."
    )

    deg = st.radio(
        "Degree Seeking",
        ["PhD", "MD/PhD", "Research Position"],
        horizontal=True,
        index=["PhD", "MD/PhD", "Research Position"].index(st.session_state.degree_seeking)
    )
    st.session_state.degree_seeking = deg

    st.divider()
    col_a, col_b = st.columns([2, 3])
    with col_a:
        if st.button("🚀 Generate Cold Email", type="primary"):
            if not st.session_state.prof_name.strip():
                st.error("⚠ Please enter the professor's name.")
            else:
                f   = st.session_state.final_focus
                deg = st.session_state.degree_seeking

                if f and f["type"] == "auto":
                    focus_block = f"""
SELECTED RESEARCH ANGLE:
- Headline: {f['headline']}
- Description: {f['description']}
- Key metabolite: {f['metabolite']}
- Key microbe: {f['microbe']}
- Pathway/gene: {f['pathway']}
- Research gap: {f['gap']}
- Research question to pose: {f['question']}"""
                elif f and f["type"] == "manual":
                    focus_block = f"""
APPLICANT'S SPECIFIC FOCUS:
{f['description']}
- Key metabolite: {f.get('metabolite') or 'derive from paper'}
- Key microbe: {f.get('microbe') or 'derive from paper'}
- Pathway/gene: {f.get('pathway') or 'derive from paper'}
- Proposed technique: {f.get('technique') or 'to be specified'}
- Research question: {f.get('question') or 'construct from above'}"""
                else:
                    focus_block = "No specific focus provided — extract the most compelling angle from the paper."

                prompt = f"""🎯 ROLE
You are an expert microbiome researcher + academic writer + PhD evaluator in Germany.
Write a highly targeted, human-sounding cold email for a {deg} application in gut microbiome research.

🎮 GOAL
The professor must feel: "This person actually read my paper carefully and thought about it like a researcher."
If the email sounds generic, templated, or robotic → FAILED.

📥 INPUTS

PAPER:
Title: {st.session_state.paper_title}
{f"Authors/Journal: {st.session_state.paper_authors}" if st.session_state.paper_authors else ""}
Content:
{st.session_state.paper_text}

{focus_block}

PROFESSOR:
Name: {st.session_state.prof_name}
University: {st.session_state.prof_univ or 'Germany'}
{f"Lab/Department: {st.session_state.prof_lab}" if st.session_state.prof_lab else ""}
{f"Research Focus: {st.session_state.prof_focus}" if st.session_state.prof_focus else ""}

APPLICANT:
Name: {st.session_state.user_name}
{f"Email: {st.session_state.user_email}" if st.session_state.user_email else ""}
Degree: {st.session_state.user_degree} from {st.session_state.user_institute}
{f"Country: {st.session_state.user_country}" if st.session_state.user_country else ""}
CV/Background:
{st.session_state.user_cv}
{f"Intended Start: {st.session_state.start_date}" if st.session_state.start_date else ""}

🧩 MANDATORY STRUCTURE

1. INTRODUCTION (3–4 natural lines)
   - Who I am ({st.session_state.user_degree})
   - My focus (gut microbiome, host interaction)
   - Tone: natural, not stiff

2. PAPER ENGAGEMENT (MOST IMPORTANT — do NOT summarize, engage deeply)
   - Reference the specific paper by title
   - Extract a specific biological insight or mechanism
   - Use exact: metabolite + microbial genus/species + pathway/gene from the selected focus
   - Add natural scientific curiosity: "What I found particularly interesting was..."
   - Show you understood WHY the result matters and what remains unclear

3. RESEARCH GAP + PRECISE QUESTION
   - Identify a real gap or unclear mechanism from the paper
   - Pose a precise scientific question that MUST include:
     • 1 specific metabolite
     • 1 microbial genus/species
     • 1 pathway or gene

4. PROPOSED RESEARCH IDEA (mini direction)
   - Suggest a specific, realistic approach
   - Include: experimental method + pathway/gene focus + expected insight
   - Keep realistic, not overambitious

5. MY EXPERIENCE (tightly connected to the idea above — NOT a generic list)
   - Use ONLY information from the CV provided
   - Directly connect specific skills/experience to the proposed idea

6. CLOSING (simple, human, short)
   - Express interest in {deg}
   - Ask for a brief discussion
   - Polite and short

🗣️ HUMAN TONE RULES
- Write like a real person
- NO: "This study demonstrates a significant association", "passionate", "cutting-edge"
- YES: "What I found particularly interesting was...", natural transitions, varied sentence length
- Max 300–350 words total

🧪 SCIENTIFIC DEPTH (mandatory)
Must include: ≥1 metabolite · ≥1 microbe · ≥1 pathway/gene · ≥1 experimental technique

🎯 SELF-CHECK — score each before outputting (refine if any < 8):
• Depth of paper usage: /10
• Human tone: /10
• Specificity: /10
• Original thinking: /10

OUTPUT FORMAT (exactly):
SCORES: depth=X/10, tone=X/10, specificity=X/10, originality=X/10
---EMAIL---
Subject: Prospective {deg} Applicant — {st.session_state.start_date or '[your intended session]'}

[Email body — no headings, no explanation]"""

                with st.spinner("Composing your email — applying scientific depth and human tone..."):
                    try:
                        raw = call_llm(prompt, max_tokens=1500)
                        st.session_state.generated_email = extract_email(raw)
                        st.session_state.scores          = parse_scores(raw)
                        go_to(5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Generation failed: {e}")

    with col_b:
        if st.button("← Back"):
            go_to(3)
            st.rerun()

# ─── STEP 5: Result ───────────────────────────────────────────────────────────
elif st.session_state.step == 5:
    st.markdown("""
    <div class="step-header">
        <div class="step-eyebrow">Step 05 — Your Email</div>
        <div class="step-title"><em>Generated</em> Cold Email</div>
        <div class="step-desc">Review, refine slightly, and send. Small personal edits always improve it.</div>
    </div>""", unsafe_allow_html=True)

    # Scores
    if st.session_state.scores:
        cols = st.columns(len(st.session_state.scores))
        for col, (label, val) in zip(cols, st.session_state.scores.items()):
            with col:
                color = "#2d6a4f" if val >= 8 else "#9a6b00" if val >= 6 else "#9b2226"
                st.markdown(f"""
                <div class="score-badge">
                    <div class="score-val" style="color:{color};">{val}/10</div>
                    <div class="score-lbl">{label}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Email display
    st.markdown(f"""
    <div class="email-output">
        <div class="email-bar">✉ Your Cold Email — {st.session_state.prof_name}</div>
        <div class="email-body">{st.session_state.generated_email}</div>
        <div class="email-footer">
        ⚠ AI-generated · Review before sending · Personal tweaks make it significantly better
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="callout-amber" style="margin-top:16px;">
    📌 <strong>Before sending:</strong> verify all scientific details against the actual paper.
    Double-check metabolite names, gene names, and pathway details — AI may occasionally hallucinate specifics.
    </div>""", unsafe_allow_html=True)

    st.divider()
    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
    with col1:
        st.download_button(
            "⬇ Download .txt",
            data=st.session_state.generated_email,
            file_name=f"cold_email_{st.session_state.prof_name.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col2:
        if st.button("🔁 Regenerate", use_container_width=True):
            go_to(4)
            st.rerun()
    with col3:
        if st.button("✏ Edit Settings", use_container_width=True):
            go_to(4)
            st.rerun()
    with col4:
        if st.button("← Edit Focus / Angle", use_container_width=True):
            go_to(2)
            st.rerun()

    # Editable copy
    with st.expander("✏ Edit email directly"):
        edited = st.text_area(
            "Edit your email",
            value=st.session_state.generated_email,
            height=400,
            label_visibility="collapsed"
        )
        if edited != st.session_state.generated_email:
            if st.button("Save edits"):
                st.session_state.generated_email = edited
                st.success("✓ Saved")
                st.rerun()
