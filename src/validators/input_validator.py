"""Input validation for security and safety."""

import re
from typing import Dict, Any
from configs.settings import MAX_INPUT_LENGTH


def input_validator(user_input: str) -> Dict[str, Any]:
    """
    Validate user input for potential security threats.

    Checks for:
    - Input length limits
    - Prompt injection attempts
    - Sensitive data exposure (emails, phones, credit cards)

    Args:
        user_input: The user's input string

    Returns:
        Dict with 'valid': bool and optional 'reason': str
    """
    # Check input length
    if len(user_input) > MAX_INPUT_LENGTH:
        return {"valid": False, "reason": "Input exceeds maximum length"}

    # Prompt injection patterns
    injection_patterns = [
        r"ignore previous instructions",
        r"reveal.*system.*prompt",
        r"override.*instructions",
        r"system.*prompt",
        r"delimiter.*injection",
        r"role.*switch",
    ]

    for pattern in injection_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return {"valid": False, "reason": "Potential prompt injection detected"}

    # Sensitive data patterns
    # Email detection
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input):
        return {"valid": False, "reason": "Email address detected in input"}

    # Phone number detection (US format)
    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', user_input):
        return {"valid": False, "reason": "Phone number detected in input"}

    # Credit card pattern detection (basic)
    if re.search(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', user_input):
        return {"valid": False, "reason": "Potential credit card information detected"}

    return {"valid": True}