# Multi-LLM API Key Support - Implementation Plan Approved

## Current Status: Plan Approved (Keep Gemini + Anthropic + others via LiteLLM)

### Step 1: Update requirements ✓
- [x] Added litellm>=1.44.7, google-generativeai>=0.8.3 to requirement.txt
- [x] pip install -r requirement.txt

### Step 2: Refactor app.py
- [ ] Add Step 0: API Setup (model select + key input)
- [ ] Abstract `get_client()` → `get_llm_client(model, api_key)`
- [ ] `call_llm(model, prompt)` replaces `call_claude()`
- [ ] LiteLLM for: kimi/moonshot-v1-8k, deepseek/deepseek-chat, qwen/Qwen2.5-7B-Instruct
- [ ] Direct: anthropic/claude-3.5-sonnet, gemini/gemini-1.5-pro

### Step 3: Test
- [ ] Test all 5 models

### Step 4: Deploy & Push

**Next:** Refactor app.py

### Step 2: Refactor app.py
- [ ] Add Step 0: API Setup (model select + key input)
- [ ] Abstract `get_client()` → `get_llm_client(model, api_key)`
- [ ] `call_llm(model, prompt)` replaces `call_claude()`
- [ ] LiteLLM for: kimi/moonshot-v1-8k, deepseek/deepseek-chat, qwen/Qwen2.5-7B-Instruct
- [ ] Direct: anthropic/claude-3.5-sonnet, gemini/gemini-1.5-pro

### Step 3: Test
- [ ] Test all 5 models with sample inputs
- [ ] Verify angle discovery + email gen

### Step 4: Deploy & Push
- [ ] Commit/push
- [ ] Update Streamlit Cloud secrets

**Next:** Implement Step 1 (requirements), then app.py refactor.

---

*Progress tracking for multi-LLM feature*
