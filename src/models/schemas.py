"""Pydantic schemas for data validation."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class CloudCartInput(BaseModel):
    """Schema for user input to the agent."""
    user_query: str


class CloudCartOutput(BaseModel):
    """Schema for agent response."""
    response: str
    data: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None


class PromptMetadata(BaseModel):
    """Metadata for prompt versions."""
    version: str
    description: str


class FewShotExample(BaseModel):
    """Schema for few-shot examples."""
    input: str
    output: str


class PromptSchema(BaseModel):
    """Complete schema for prompt configuration."""
    metadata: PromptMetadata
    system_prompt: str
    few_shot_examples: List[FewShotExample]
    input_schema: Dict[str, Any]