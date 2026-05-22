"""CloudCart support agent implementation."""

import re
from typing import Dict, Any
from pathlib import Path

from src.prompts.prompt_manager import PromptManager
from src.validators.input_validator import input_validator
from src.validators.output_validator import output_validator
from src.models.schemas import CloudCartOutput
from src.utils.logger import setup_logger

from src.database.db import (
    get_orders_by_customer,
    get_order_items
)

logger = setup_logger()

CURRENT_CUSTOMER_ID = "user-001"

ORDER_PATTERNS = [
    r"\border\b",
    r"\borders\b",
    r"\btrack\b",
    r"\bshipping\b",
    r"\bdelivery\b",
    r"\bstatus\b",
    r"\bhistory\b",

    # Shopping / purchase intent
    r"\bbuy\b",
    r"\bbought\b",
    r"\bpurchase\b",
    r"\bpurchased\b",

    # Generic commerce wording
    r"\bitem\b",
    r"\bitems\b",
    r"\bproduct\b",
    r"\bstuff\b",

    # Product names
    r"\bshirt\b",
    r"\bt-shirt\b",
    r"\bmug\b",
    r"\bbackpack\b",
    r"\bcap\b",
    r"\bsocks\b",

    # Account/order exploration
    r"\brecent\b",
    r"\blatest\b",
    r"\bcancelled\b",
    r"\bdelivered\b",
    r"\bpreparing\b",
    r"\bshipped\b",
]


def is_order_query(user_input: str) -> bool:
    normalized = user_input.lower()

    if (
        "order" in normalized
        or "orders" in normalized
        or "track" in normalized
    ):
        return True

    for pattern in ORDER_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True

    return False


def build_order_context(user_input: str) -> str:
    """
    Build factual order context from database records.

    This function retrieves structured business data
    for the LLM to reason over.
    """

    user_orders = get_orders_by_customer(CURRENT_CUSTOMER_ID)

    if not user_orders:
        return "No customer orders found."

    context_lines = []
    context_lines.append("Customer Order Data:\n")

    for order in user_orders:

        order["items"] = get_order_items(order["order_id"])

        context_lines.append(
            f"Order ID: {order['order_id']}"
        )

        context_lines.append(
            f"Status: {order['status']}"
        )

        context_lines.append(
            f"Ordered At: {order['ordered_at']}"
        )

        context_lines.append(
            f"Order Total: {order['total']} {order['currency']}"
        )

        if order.get("delivered_at"):
            context_lines.append(
                f"Delivered At: {order['delivered_at']}"
            )

        if order.get("estimated_delivery"):
            context_lines.append(
                f"Estimated Delivery: {order['estimated_delivery']}"
            )

        context_lines.append("Items:")

        for item in order["items"]:

            context_lines.append(
                f"- SKU: {item['sku']}"
            )

            context_lines.append(
                f"  Product: {item['name']}"
            )

            context_lines.append(
                f"  Quantity: {item['quantity']}"
            )

            context_lines.append(
                f"  Price: {item['price']}"
            )

        context_lines.append("")

    return "\n".join(context_lines)


def safe_cloudcart_agent(user_input: str) -> Dict[str, Any]:
    """
    Safe CloudCart support agent with validation pipeline.

    Pipeline:
    1. Validate input
    2. Load and compile prompt
    3. Invoke LLM
    4. Validate output
    5. Return structured response

    Args:
        user_input: User's query string

    Returns:
        Dict with status, response, and metadata
    """

    try:

        logger.info("Processing user input")

        # ==========================================
        # Step 1: Validate RAW user input
        # ==========================================

        validation = input_validator(user_input)

        if not validation["valid"]:

            logger.warning(
                f"Input validation failed: {validation['reason']}"
            )

            return {
                "status": "blocked",
                "error": validation["reason"],
                "input_validation": validation
            }

        # ==========================================
        # Step 1.5: Build grounded order context
        # ==========================================

        grounded_context = ""

        if is_order_query(user_input):

            logger.info(
                "Detected order query; building grounded order context"
            )

            grounded_context = build_order_context(user_input)

        # ==========================================
        # Step 2: Load prompt
        # ==========================================

        prompt_dir = Path("prompts/cloudcart")

        pm = PromptManager(prompt_dir)

        schema = pm.load("current")

        prompt = pm.compile(schema)

        # ==========================================
        # Step 3: Build final grounded prompt input
        # ==========================================

        final_prompt_input = user_input

        if grounded_context:

            final_prompt_input = f"""
Customer Order Context:
{grounded_context}

User Query:
{user_input}
"""

        # ==========================================
        # Step 4: Invoke LLM
        # ==========================================

        logger.info("Invoking LLM")

        response_text = pm.invoke(
            prompt,
            {"user_query": final_prompt_input},
            schema,
            validation_input={
                "user_query": user_input
                }
                )

        # ==========================================
        # Step 5: Output validation
        # ==========================================

        out_validation = output_validator(response_text)

        if not out_validation["valid"]:

            logger.warning(
                f"Output validation failed: {out_validation['reason']}"
            )

            return {
                "status": "failed",
                "error": out_validation["reason"],
                "output_validation": out_validation
            }

        # ==========================================
        # Step 6: Structured response
        # ==========================================

        output = CloudCartOutput(response=response_text)

        logger.info("Agent response generated successfully")

        prompt_version = "unknown"

        if schema is not None:

            if hasattr(schema, "metadata"):

                prompt_version = getattr(
                    schema.metadata,
                    "version",
                    "unknown"
                )

            elif isinstance(schema, dict):

                prompt_version = schema.get(
                    "metadata",
                    {}
                ).get(
                    "version",
                    "unknown"
                )

        return {
            "status": "success",
            "response": output.model_dump(),
            "input_validation": validation,
            "output_validation": out_validation,
            "prompt_version": prompt_version
        }

    except Exception as e:

        logger.error(
            f"Error in safe_cloudcart_agent: {e}"
        )

        return {
            "status": "error",
            "error": f"Internal error: {str(e)}"
        }