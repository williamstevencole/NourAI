"""LLM Factory - Provider selection for Ollama, Groq, and OpenRouter."""

from typing import Optional

from config import (
    LLM_PROVIDER,
    TEMPERATURE,
    MAX_TOKENS,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_APP_NAME,
    OPENROUTER_APP_URL,
)


def get_llm(temperature: Optional[float] = None, max_tokens: Optional[int] = None):
    """Get the configured LLM instance based on LLM_PROVIDER."""
    temp = temperature if temperature is not None else TEMPERATURE
    tokens = max_tokens if max_tokens is not None else MAX_TOKENS

    if LLM_PROVIDER == "local":
        from langchain_community.llms.ollama import Ollama
        return Ollama(model=OLLAMA_MODEL, temperature=temp, base_url=OLLAMA_BASE_URL)

    elif LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment.")
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=GROQ_MODEL,
            temperature=temp,
            max_tokens=tokens,
            groq_api_key=GROQ_API_KEY
        )

    elif LLM_PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set in environment.")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=OPENROUTER_MODEL,
            temperature=temp,
            max_tokens=tokens,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": OPENROUTER_APP_URL,
                "X-Title": OPENROUTER_APP_NAME,
            }
        )

    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER: '{LLM_PROVIDER}'. "
            f"Must be 'local', 'groq', or 'openrouter'"
        )
