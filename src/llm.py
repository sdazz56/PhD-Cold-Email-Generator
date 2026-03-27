import streamlit as st
import litellm

# LiteLLM Configuration
litellm.drop_params = True  # Ignore unsupported params like 'top_p' for some models

def get_model_mapping(model_name: str) -> str:
    """Map UI model names to LiteLLM compatible model strings."""
    mapping = {
        "anthropic/claude-3-5-sonnet-20240620": "anthropic/claude-3-5-sonnet-20240620",
        "anthropic/claude-opus-4-6": "anthropic/claude-3-opus-20240229", # Mapping future to current
        "anthropic/claude-sonnet-4-6": "anthropic/claude-3-5-sonnet-20240620",
        "anthropic/claude-haiku-4-5-20251001": "anthropic/claude-3-haiku-20240307",
        "gemini/gemini-1.5-flash": "gemini/gemini-1.5-flash",
        "gemini/gemini-1.5-pro": "gemini/gemini-1.5-pro",
        "gemini/gemini-3.1-pro-preview": "gemini/gemini-1.5-pro",
        "gemini/gemini-3-flash-preview": "gemini/gemini-1.5-flash",
        "gemini/gemini-flash-lite-latest": "gemini/gemini-1.5-flash",
        "openai/gpt-5.4-2026-03-05": "openai/gpt-4o",
        "openai/gpt-5.4-mini-2026-03-17": "openai/gpt-4o-mini",
        "openai/gpt-5.4-nano-2026-03-17": "openai/gpt-4o-mini",
        "openai/gpt-4o": "openai/gpt-4o",
        "moonshot-v1-8k": "moonshot/moonshot-v1-8k",
        "deepseek-chat": "deepseek/deepseek-chat",
        "qwen2.5-7b-instruct": "huggingface/qwen/Qwen2.5-7B-Instruct"
    }
    # If it's a manual entry or already has a provider prefix, return as is
    if "/" in model_name:
        return model_name
    return mapping.get(model_name, model_name)

def call_llm(prompt: str, max_tokens: int = 1500) -> str:
    """Unified LLM call using LiteLLM."""
    model_name = st.session_state.api_model
    api_key = st.session_state.api_key.strip() # Strip any accidental whitespace
    
    if not api_key:
        st.error("❌ API key missing. Please set it in Step 0.")
        st.stop()
    
    target_model = get_model_mapping(model_name)
    
    try:
        # Pass api_key directly to completion() for better reliability
        response = litellm.completion(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            api_key=api_key
        )
        return response.choices[0].message.content

    except Exception as e:
        err_msg = str(e).lower()
        if "401" in err_msg or "invalid_api_key" in err_msg or "invalid key" in err_msg or "authentication" in err_msg:
            st.error("❌ Invalid API Key. Please check your key in Step 0.")
        elif "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg:
            st.error("❌ Quota Exhausted. You've hit your API limit or billing issue.")
        elif "404" in err_msg or "not_found" in err_msg:
            # Re-check mapping if 404
            st.error(f"❌ Model Not Found: The model `{target_model}` is not available for your API key or region.")
        else:
            st.error(f"❌ LLM Error: {str(e)}")
        st.stop()
        return ""
