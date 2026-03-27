import streamlit as st
import json

try:
    import litellm
except ImportError as e:
    st.error(f"❌ Missing dependency: `{e.name}`\n\nPlease run: `pip install -r requirements.txt` or ensure you have selected the correct virtual environment in your IDE.")
    st.stop()

# Modular imports
from src.styles import apply_custom_css
from src.utils import go_to, parse_scores, extract_email, sanitize
from src.llm import call_llm
from src.prompts import get_angle_discovery_prompt, get_email_generation_prompt

# ─── Provider Configuration ────────────────────────────────────────────────────────
PROVIDERS = {
    "Gemini": {
        "models": [
            {"id": "gemini/gemini-1.5-flash", "label": "Gemini 1.5 Flash (fastest)"},
            {"id": "gemini/gemini-1.5-pro", "label": "Gemini 1.5 Pro (smartest)"},
            {"id": "gemini/gemini-3.1-pro-preview", "label": "Gemini 3.1 Pro (best)"},
            {"id": "gemini/gemini-3-flash-preview", "label": "Gemini 3.0 Flash (fast)"},
            {"id": "gemini/gemini-flash-lite-latest", "label": "Gemini Flash Lite (cheap)"}
        ],
        "placeholder": "AIza... — Google AI Studio key"
    },
    "OpenAI": {
        "models": [
            {"id": "openai/gpt-5.4-2026-03-05", "label": "GPT-5.4 (best)"},
            {"id": "openai/gpt-5.4-mini-2026-03-17", "label": "GPT-5.4 mini (fast)"},
            {"id": "openai/gpt-5.4-nano-2026-03-17", "label": "GPT-5.4 nano (fast)"},
            {"id": "openai/gpt-4o", "label": "GPT-4o (legacy best)"}
        ],
        "placeholder": "sk-... — OpenAI API key"
    },
    "Anthropic": {
        "models": [
            {"id": "anthropic/claude-3-5-sonnet-20240620", "label": "Claude 3.5 Sonnet (balanced)"},
            {"id": "anthropic/claude-opus-4-6", "label": "Claude Opus 4 (best)"},
            {"id": "anthropic/claude-sonnet-4-6", "label": "Claude Sonnet 4 (balanced)"},
            {"id": "anthropic/claude-haiku-4-5-20251001", "label": "Claude Haiku 4 (fast)"}
        ],
        "placeholder": "sk-ant-... — Anthropic API key"
    },
    "Other": {
        "models": [
            {"id": "deepseek-chat", "label": "Deepseek Chat (V3)"},
            {"id": "qwen2.5-7b-instruct", "label": "Qwen 2.5 7B"},
            {"id": "moonshot-v1-8k", "label": "Moonshot V1"},
            {"id": "Manual Entry", "label": "Manual Entry..."}
        ],
        "placeholder": "Your API Key"
    }
}

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhD Cold Email Generator",
    page_icon="🧫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
apply_custom_css()

# ─── Session state init ────────────────────────────────────────────────────────
defaults = {
    "step": 0,
    "api_model": "anthropic/claude-3-5-sonnet-20240620",
    "api_key": "",
    "provider_keys": {
        "Gemini": "",
        "OpenAI": "",
        "Anthropic": "",
        "Other": ""
    },
    "paper_title": "",
    "paper_authors": "",
    "paper_text": "",
    "paper_field": "Academic",
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
        <div class="step-title">Choose Your <em>AI Provider</em> & Model</div>
        <div class="step-desc">Select your preferred AI engine to unlock generation.</div>
    </div>""", unsafe_allow_html=True)


    # Provider Selection (Radio styled as tabs)
    provider_names = list(PROVIDERS.keys())
    selected_provider = st.radio(
        "Select Provider",
        provider_names,
        horizontal=True,
        label_visibility="collapsed"
    )

    # UI for Selected Provider
    p_data = PROVIDERS[selected_provider]
    p_models = p_data.get("models", [])
    
    col1, col2 = st.columns(2)
    with col1:
        model_labels = []
        model_ids = []
        for model_item in p_models:
            if isinstance(model_item, dict):
                model_labels.append(model_item.get("label", "Unknown"))
                model_ids.append(model_item.get("id", "Manual"))
        
        selected_label = st.selectbox(
            f"{selected_provider} Model",
            model_labels,
            index=0,
            help=f"Choose the engine from {selected_provider}"
        )
        
        # Get matching ID
        idx = model_labels.index(selected_label)
        target_id = model_ids[idx]
        if target_id == "Manual Entry":
            target_id = st.text_input("Enter Model Name (e.g. together/llama-3)", placeholder="provider/model-name")
        
        st.session_state.api_model = target_id

    with col2:
        # Load the key for this provider from session state if it exists
        current_key = st.session_state.provider_keys.get(selected_provider, "")
        
        new_key = st.text_input(
            f"{selected_provider} API Key",
            value=current_key,
            type="password",
            placeholder=p_data.get("placeholder", ""),
            help=f"Enter your {selected_provider} API key"
        )
        # Update session state
        st.session_state.provider_keys[selected_provider] = new_key
        st.session_state.api_key = new_key

    st.markdown("""
    <div class="callout-green">
    🔑 <strong>API Keys stay with you.</strong> Keys are used locally for this session and not stored permanently on any server.
    </div>""", unsafe_allow_html=True)

    if st.button("✅ Verify & Start!", type="primary", use_container_width=True):
        if not st.session_state.api_key.strip():
            st.error("⚠️ Please enter your API key to continue.")
        else:
            with st.spinner("Verifying connection... (usually 2-5 seconds)"):
                try:
                    # Unified verification call
                    test_prompt = "Hello, respond with 'OK'."
                    call_llm(test_prompt, max_tokens=10)
                    
                    st.session_state.step = 1
                    st.success("✅ Connection successful!")
                    st.rerun()
                except Exception as e:
                    err_msg = str(e).lower()
                    if "401" in err_msg or "invalid_api_key" in err_msg or "invalid key" in err_msg:
                        st.error("❌ Invalid API Key. Please verify and try again.")
                    elif "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg:
                        st.error("❌ Quota Exhausted. Check your billing dashboard.")
                    else:
                        st.error(f"❌ Connection Failed: {str(e)}")

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
        elif len(st.session_state.paper_text.strip().split()) < 300:
            st.error("⚠ Please paste more paper content — at least 300 words (abstract and key findings).")
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
                with st.spinner("Identifying research field and extracting angles... (30-60s)"):
                    # Phase 1: Identify Field (Quick call)
                    field_prompt = f"Identify the primary scientific field of this research paper in 2-3 words (e.g. 'Microbiology', 'Computer Science', 'Materials Science').\n\nTITLE: {st.session_state.paper_title}\n\nCONTENT: {st.session_state.paper_text[:2000]}"
                    try:
                        detected_field = call_llm(field_prompt, max_tokens=10).strip().replace("'", "").replace('"', "")
                        st.session_state.paper_field = detected_field
                    except:
                        st.session_state.paper_field = "Academic"

                    # Phase 2: Discover Angles
                    prompt = get_angle_discovery_prompt(
                        st.session_state.paper_title,
                        st.session_state.paper_authors,
                        st.session_state.paper_text,
                        st.session_state.cv_brief,
                        field=st.session_state.paper_field
                    )
                    try:
                        raw = call_llm(prompt, max_tokens=1200)
                        clean = raw.replace("```json", "").replace("```", "").strip()
                        parsed = json.loads(clean)
                        st.session_state.angles = parsed.get("angles", [])
                        st.session_state.selected_angle_idx = 0
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        st.rerun()

        # Show angles
        if st.session_state.angles:
            # Use detected field if available, else derive
            field = st.session_state.paper_field or "Academic"
            st.markdown(f"#### Select a Research Angle (Field: {sanitize(field)})")
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
                    <div class="angle-headline">{sanitize(a['headline'])}</div>
                    <div class="angle-body">{sanitize(a['description'])}</div>
                    <div style="font-size:12px; color:#706a5c; margin-bottom:6px;">
                        <strong style="color:#1a1916;">Gap:</strong> {sanitize(a['gap'])}
                    </div>
                    <div class="angle-question">❓ {sanitize(a['question'])}</div>
                    <span class="tag tag-metabolite">⚗ {sanitize(a['metabolite'])}</span>
                    <span class="tag tag-microbe">🦠 {sanitize(a['microbe'])}</span>
                    <span class="tag tag-pathway">🔬 {sanitize(a['pathway'])}</span>
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
                if st.button("← Back to Paper", key="back_to_paper_1"):
                    go_to(1)
                    st.rerun()
        else:
            if st.button("← Back to Paper", key="back_to_paper_2"):
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
                placeholder="e.g. Describe the mechanism, metabolite, and microbe focus..."
            )
            metabolite = st.text_input("Key Metabolite(s)", placeholder="e.g. butyrate, propionate")
            microbe    = st.text_input("Key Microbe(s)", placeholder="e.g. Faecalibacterium prausnitzii")

        with col2:
            pathway   = st.text_input("Pathway / Gene", placeholder="e.g. GPR109A / NF-κB / HIF-1α")
            technique = st.text_input("Your Proposed Technique", placeholder="e.g. LC-MS, anaerobic fermentation")
            question  = st.text_area(
                "Research Question to Pose",
                height=120,
                placeholder="e.g. Does X modulate Y in Z model?"
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
            if st.button("← Back to Paper", key="back_to_paper_manual"):
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
        placeholder="Paste your most relevant experience, projects, and skills here."
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
        if st.button("← Back", key="back_to_focus"):
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
        placeholder="e.g. Gut microbiome-immune crosstalk, IBD mechanisms..."
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
- Key molecule: {f['metabolite']}
- Key subject: {f['microbe']}
- Pathway/mechanism: {f['pathway']}
- Research gap: {f['gap']}
- Research question: {f['question']}"""
                elif f and f["type"] == "manual":
                    focus_block = f"""
APPLICANT'S SPECIFIC FOCUS:
{f['description']}
- Key molecule: {f.get('metabolite') or 'derive from paper'}
- Key subject: {f.get('microbe') or 'derive from paper'}
- Pathway/mechanism: {f.get('pathway') or 'derive from paper'}
- Proposed technique: {f.get('technique') or 'to be specified'}
- Research question: {f.get('question') or 'construct from above'}"""
                else:
                    focus_block = "No specific focus provided."

                prompt = get_email_generation_prompt(
                    deg,
                    {
                        "paper_title": st.session_state.paper_title,
                        "paper_authors": st.session_state.paper_authors,
                        "paper_text": st.session_state.paper_text,
                        "prof_name": st.session_state.prof_name,
                        "prof_univ": st.session_state.prof_univ,
                        "prof_lab": st.session_state.prof_lab,
                        "prof_focus": st.session_state.prof_focus,
                        "user_name": st.session_state.user_name,
                        "user_email": st.session_state.user_email,
                        "user_degree": st.session_state.user_degree,
                        "user_institute": st.session_state.user_institute,
                        "user_country": st.session_state.user_country,
                        "user_cv": st.session_state.user_cv,
                        "start_date": st.session_state.start_date,
                    },
                    focus_block,
                    field=st.session_state.paper_field
                )

                with st.spinner("Composing your email — applying scientific depth... (30-60s)"):
                    try:
                        raw = call_llm(prompt, max_tokens=1500)
                        st.session_state.generated_email = extract_email(raw)
                        st.session_state.scores          = parse_scores(raw)
                        go_to(5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Generation failed: {str(e)}")
                        st.rerun()

    with col_b:
        if st.button("← Back", key="back_to_profile"):
            go_to(3)
            st.rerun()

# ─── STEP 5: Result ───────────────────────────────────────────────────────────
elif st.session_state.step == 5:
    st.markdown("""
    <div class="step-header">
        <div class="step-eyebrow">Step 05 — Your Email</div>
        <div class="step-title"><em>Generated</em> Cold Email</div>
        <div class="step-desc">Review, refine slightly, and send.</div>
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
        <div class="email-bar">✉ Your Cold Email — {sanitize(st.session_state.prof_name)}</div>
        <div class="email-body">{sanitize(st.session_state.generated_email)}</div>
        <div class="email-footer">
        ⚠ AI-generated · Review before sending
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
