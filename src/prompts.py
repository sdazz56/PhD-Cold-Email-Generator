def get_angle_discovery_prompt(paper_title, paper_authors, paper_text, cv_brief, field="biomedical"):
    return f"""You are an expert {field} researcher. Carefully read this research paper and extract 3 distinct, highly specific research angles that a PhD applicant could use as the focus of a cold email.

PAPER TITLE: {paper_title}
{f"AUTHORS/JOURNAL: {paper_authors}" if paper_authors else ""}

PAPER CONTENT:
{paper_text}

{f"APPLICANT CV (for relevance ranking):{chr(10)}{cv_brief}" if cv_brief else ""}

For each angle extract:
1. A short compelling headline (max 12 words)
2. A 2-3 sentence description of the specific insight or gap
3. The key scientific element (e.g. metabolite/molecule/variable)
4. The key subject/model (e.g. microbe/cell line/algorithm)
5. The relevant pathway or gene (or core mechanism)
6. Why this is still unclear (the gap)
7. A precise research question (1 sentence, must include key element + subject + mechanism)

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

def get_email_generation_prompt(deg, inputs, focus_block, field="academic"):
    return f"""🎯 ROLE
You are an expert {field} researcher + academic writer + PhD evaluator.
Write a highly targeted, human-sounding cold email for a {deg} application.

🎮 GOAL
The professor must feel: "This person actually read my paper carefully and thought about it like a researcher."
If the email sounds generic, templated, or robotic → FAILED.

📥 INPUTS

PAPER:
Title: {inputs['paper_title']}
{f"Authors/Journal: {inputs['paper_authors']}" if inputs['paper_authors'] else ""}
Content (summarized):
{inputs['paper_text'][:3000]}

{focus_block}

PROFESSOR:
Name: {inputs['prof_name']}
University: {inputs['prof_univ'] or 'Germany'}
{f"Lab/Department: {inputs['prof_lab']}" if inputs['prof_lab'] else ""}
{f"Research Focus: {inputs['prof_focus']}" if inputs['prof_focus'] else ""}

APPLICANT:
Name: {inputs['user_name']}
{f"Email: {inputs['user_email']}" if inputs['user_email'] else ""}
Degree: {inputs['user_degree']} from {inputs['user_institute']}
{f"Country: {inputs['user_country']}" if inputs['user_country'] else ""}
CV/Background:
{inputs['user_cv']}
{f"Intended Start: {inputs['start_date']}" if inputs['start_date'] else ""}

🧩 MANDATORY STRUCTURE

1. INTRODUCTION (3–4 natural lines)
   - Who I am ({inputs['user_degree']})
   - Tone: natural, not stiff

2. PAPER ENGAGEMENT (MOST IMPORTANT — do NOT summarize, engage deeply)
   - Reference the specific paper by title
   - Extract a specific scientific insight or mechanism
   - Use exact terms (metabolite/microbe/pathway) from the selected focus
   - Add natural scientific curiosity: "What I found particularly interesting was..."
   - Show you understood WHY the result matters and what remains unclear

3. RESEARCH GAP + PRECISE QUESTION
   - Identify a real gap or unclear mechanism from the paper
   - Pose a precise scientific question that includes the specific elements of the paper

4. PROPOSED RESEARCH IDEA (mini direction)
   - Suggest a specific, realistic approach
   - Include: experimental method + specific focus + expected insight

5. MY EXPERIENCE (tightly connected to the idea above — NOT a generic list)
   - Use ONLY information from the CV provided
   - Directly connect specific skills/experience to the proposed idea

6. CLOSING (simple, human, short)

🗣️ HUMAN TONE RULES
- Write like a real person
- NO buzzwords like: "significant association", "passionate", "cutting-edge"
- YES: "What I found particularly interesting was...", natural transitions
- Max 300–350 words total

🧪 SCIENTIFIC DEPTH (mandatory)
Must include: ≥1 key element · ≥1 subject/model · ≥1 mechanism · ≥1 experimental technique

🎯 SELF-CHECK — score each before outputting (refine if any < 8):
• Depth of paper usage: /10
• Human tone: /10
• Specificity: /10
• Original thinking: /10

OUTPUT FORMAT (exactly):
SCORES: depth=X/10, tone=X/10, specificity=X/10, originality=X/10
---EMAIL---
Subject: Prospective {deg} Applicant — {inputs['start_date'] or '[intended session]'}

[Email body — no headings, no explanation]"""
