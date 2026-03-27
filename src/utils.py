import streamlit as st
import re

import html

def go_to(step: int):
    st.session_state.step = step

def parse_scores(raw: str) -> dict:
    # Try multiple regex patterns for robustness
    patterns = [
        r"SCORES:\s*depth=(\d+)/10,\s*tone=(\d+)/10,\s*specificity=(\d+)/10,\s*originality=(\d+)/10",
        r"depth=(\d+),\s*tone=(\d+),\s*specificity=(\d+),\s*originality=(\d+)",
        r"depth:\s*(\d+)/10,\s*tone:\s*(\d+)/10"
    ]
    
    for p in patterns:
        m = re.search(p, raw, re.IGNORECASE)
        if m:
            try:
                scores = {
                    "Paper Depth": int(m.group(1)),
                    "Human Tone":  int(m.group(2)),
                }
                if m.lastindex >= 4:
                    scores["Specificity"] = int(m.group(3))
                    scores["Originality"] = int(m.group(4))
                return scores
            except (ValueError, IndexError):
                continue
    return {}

def extract_email(raw: str) -> str:
    if "---EMAIL---" in raw:
        return raw.split("---EMAIL---", 1)[1].strip()
    # Fallback: strip score line if it's the first line
    lines = raw.strip().split("\n")
    if len(lines) > 0 and "SCORES:" in lines[0].upper():
        return "\n".join(lines[1:]).strip()
    return raw.strip()

def sanitize(text: str) -> str:
    return html.escape(str(text))
