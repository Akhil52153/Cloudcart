"""Configuration settings for CloudCart."""

from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")

# LLM Configuration
LLM_MODEL: str = "llama-3.1-8b-instant"
LLM_TEMPERATURE: float = 0.0

# Platform Configuration
PLATFORM_NAME: str = "CloudCart"
SUPPORT_TIER: str = "Premium"

# Validation Limits
MAX_INPUT_LENGTH: int = 500