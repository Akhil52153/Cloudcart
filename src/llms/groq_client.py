"""Groq LLM client configuration."""

from langchain_groq import ChatGroq
from configs.settings import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE


def get_llm() -> ChatGroq:
    """Create and return a configured ChatGroq instance."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
    )