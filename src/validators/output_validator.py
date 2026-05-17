"""Output validation for safety and compliance."""

import re
from typing import Dict, Any


def output_validator(output: str) -> Dict[str, Any]:
    """
    Validate LLM output for potential security issues.

    Checks for:
    - Prompt leakage
    - Hallucinated data
    - Out-of-scope responses
    - Policy violations

    Args:
        output: The LLM response string

    Returns:
        Dict with 'valid': bool and optional 'reason': str
    """
    # Check for prompt leakage
    leakage_patterns = [
        r"system prompt",
        r"ignore instructions",
        r"internal instructions",
    ]

    for pattern in leakage_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            return {"valid": False, "reason": "Potential prompt leakage detected"}

    # Check for hallucinated product data
    # Simple heuristic: mentions of products with prices or availability
    hallucination_patterns = [
        r"\$\d+",  # Dollar amounts
        r"available now|in stock|out of stock",  # Availability claims
        r"product.*cost|cost.*product",  # Product costs
    ]
    
    for pattern in hallucination_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            return {"valid": False, "reason": "Potential hallucinated product data"}

    # Check for out-of-scope content
    out_of_scope_patterns = [
        r"poli",  # politics, political
        r"religio",  # religion, religious
        r"controversial",
    ]
    for pattern in out_of_scope_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            return {"valid": False, "reason": f"Out-of-scope content detected: {pattern}"}

    # Policy violations (example: no refunds mentioned inappropriately)
    # This is a placeholder for more specific policies

    return {"valid": True}