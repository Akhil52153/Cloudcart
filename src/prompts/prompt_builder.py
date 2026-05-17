"""Prompt building utilities."""

from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from src.models.schemas import PromptSchema
from configs.settings import PLATFORM_NAME, SUPPORT_TIER


def build_chat_prompt(schema: PromptSchema) -> ChatPromptTemplate:
    """
    Build a ChatPromptTemplate from a PromptSchema.

    Uses partial substitution for platform_name and support_tier.

    Args:
        schema: The prompt schema

    Returns:
        Configured ChatPromptTemplate
    """
    messages = []

    # System message with template variables
    system_message = SystemMessagePromptTemplate.from_template(schema.system_prompt)
    messages.append(system_message)

    # Few-shot examples
    for example in schema.few_shot_examples:
        messages.append(HumanMessagePromptTemplate.from_template(example.input))
        messages.append(AIMessagePromptTemplate.from_template(example.output))  # AI responses

    # User input placeholder
    human_message = HumanMessagePromptTemplate.from_template("{user_query}")
    messages.append(human_message)

    # Create ChatPromptTemplate and apply partial
    prompt = ChatPromptTemplate.from_messages(messages)
    prompt = prompt.partial(
        platform_name=PLATFORM_NAME,
        support_tier=SUPPORT_TIER
    )
    return prompt