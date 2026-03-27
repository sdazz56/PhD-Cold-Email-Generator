import streamlit as st

def apply_custom_css():
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
    color: rgba(255,255,255,0.7) !important;
    font-size: 13px !important;
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
    background: white !important;
    color: #1a1916 !important;
    border: 1.5px solid #ddd8cc !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    -webkit-text-fill-color: #1a1916 !important;
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
