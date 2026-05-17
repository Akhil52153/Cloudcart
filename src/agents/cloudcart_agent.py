"""CloudCart support agent implementation."""

import re
from typing import Dict, Any, List
from pathlib import Path
from src.prompts.prompt_manager import PromptManager
from src.validators.input_validator import input_validator
from src.validators.output_validator import output_validator
from src.models.schemas import CloudCartOutput
from src.utils.logger import setup_logger

logger = setup_logger()

CURRENT_CUSTOMER_ID = "user-001"
DUMMY_ORDERS = [
    {
        "customer_id": "user-001",
        "order_id": "CART-1001",
        "status": "Delivered",
        "total": 89.99,
        "currency": "USD",
        "ordered_at": "2026-05-01",
        "delivered_at": "2026-05-05",
        "items": [
            {"sku": "CC-SHIRT-01", "name": "CloudCart T-shirt", "quantity": 2, "price": 24.99},
            {"sku": "CC-MUG-02", "name": "CloudCart Coffee Mug", "quantity": 1, "price": 39.99}
        ]
    },
    {
        "customer_id": "user-001",
        "order_id": "CART-1002",
        "status": "Preparing",
        "total": 35.49,
        "currency": "USD",
        "ordered_at": "2026-05-10",
        "estimated_delivery": "2026-05-16",
        "items": [
            {"sku": "CC-SOCK-05", "name": "CloudCart Socks Pack", "quantity": 3, "price": 11.83}
        ]
    },
    {
        "customer_id": "user-002",
        "order_id": "CART-2001",
        "status": "Shipped",
        "total": 125.00,
        "currency": "USD",
        "ordered_at": "2026-04-25",
        "estimated_delivery": "2026-05-02",
        "items": [
            {"sku": "CC-BAG-03", "name": "CloudCart Backpack", "quantity": 1, "price": 125.00}
        ]
    }
]

ORDER_PATTERNS = [
    r"\border\b",
    r"\borders\b",
    r"\btrack\b",
    r"\bshipping\b",
    r"\bdelivery\b",
    r"\bstatus\b",
    r"\bhistory\b"
]


def is_order_query(user_input: str) -> bool:
    normalized = user_input.lower()
    if "order" in normalized or "orders" in normalized or "track" in normalized:
        return True
    for pattern in ORDER_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True
    return False


def format_order(order: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"**Order ID:** `{order['order_id']}`")
    lines.append(f"**Status:** {order['status']}")
    lines.append(f"**Placed Date:** {order['ordered_at']}")
    
    if order.get("delivered_at"):
        lines.append(f"**Delivery Date:** {order['delivered_at']}")
    elif order.get("estimated_delivery"):
        lines.append(f"**Estimated Delivery:** {order['estimated_delivery']}")

    lines.append("\n**Items:**")
    for item in order["items"]:
        lines.append(f"- {item['quantity']}x {item['name']} (${item['price']:.2f})")
    
    lines.append(f"\n**Total:** ${order['total']:.2f} {order['currency']}")
    return "\n".join(lines)


def build_order_response(user_input: str) -> Dict[str, Any]:
    user_orders = [order for order in DUMMY_ORDERS if order["customer_id"] == CURRENT_CUSTOMER_ID]
    if not user_orders:
        return {
            "status": "success",
            "response": {
                "response": "I could not find any recent orders for you right now.",
                "data": {"orders": []}
            },
            "input_validation": {"valid": True},
            "output_validation": {"valid": True, "reason": "No orders found"},
            "prompt_version": "structured-order-handler"
        }

    normalized = user_input.lower()
    
    # 1. Specific Order ID requested
    mentioned_orders = [o for o in user_orders if o['order_id'].lower() in normalized]
    if mentioned_orders:
        order_sections = [format_order(o) for o in mentioned_orders]
        response_text = "Here are the details for your requested order:\n\n" + "\n\n---\n\n".join(order_sections)
        
    # 2. Only IDs requested
    elif "id" in normalized and ("recent" in normalized or "my" in normalized or "give me" in normalized):
        ids = [f"- `{o['order_id']}` ({o['status']})" for o in user_orders]
        response_text = "Here are your recent order IDs:\n\n" + "\n".join(ids)
        
    # 3. Generic status query without ID
    elif "where" in normalized or "status" in normalized:
        response_text = "I'd be happy to check your order status. Could you please provide your specific Order ID (e.g., `CART-1001`)?"
        
    # 4. Fallback (all recent orders)
    else:
        order_sections = [format_order(order) for order in user_orders]
        response_text = "Here are your recent CloudCart orders:\n\n" + "\n\n---\n\n".join(order_sections)

    return {
        "status": "success",
        "response": {
            "response": response_text,
            "data": {"orders": user_orders}
        },
        "input_validation": {"valid": True},
        "output_validation": {"valid": True, "reason": "Structured order response provided"},
        "prompt_version": "structured-order-handler"
    }


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

        # Step 1: Input validation
        validation = input_validator(user_input)
        if not validation["valid"]:
            logger.warning(f"Input validation failed: {validation['reason']}")
            return {
                "status": "blocked",
                "error": validation["reason"],
                "input_validation": validation
            }

        # Step 1.5: Structured order data handling
        if is_order_query(user_input):
            logger.info("Detected order query; returning structured order data")
            return build_order_response(user_input)

        # Step 2: Load prompt
        prompt_dir = Path("prompts/cloudcart")
        pm = PromptManager(prompt_dir)
        schema = pm.load("current")
        prompt = pm.compile(schema)

        # Step 3: Invoke LLM (now passing schema for validation per C.3)
        logger.info("Invoking LLM")
        response_text = pm.invoke(prompt, {"user_query": user_input}, schema)

        # Step 4: Output validation
        out_validation = output_validator(response_text)
        if not out_validation["valid"]:
            logger.warning(f"Output validation failed: {out_validation['reason']}")
            return {
                "status": "failed",
                "error": out_validation["reason"],
                "output_validation": out_validation
            }

        # Step 5: Return structured response
        output = CloudCartOutput(response=response_text)
        logger.info("Agent response generated successfully")

        prompt_version = "unknown"
        if schema is not None:
            if hasattr(schema, "metadata"):
                prompt_version = getattr(schema.metadata, "version", "unknown")
            elif isinstance(schema, dict):
                prompt_version = schema.get("metadata", {}).get("version", "unknown")

        return {
            "status": "success",
            "response": output.model_dump(),
            "input_validation": validation,
            "output_validation": out_validation,
            "prompt_version": prompt_version
        }

    except Exception as e:
        logger.error(f"Error in safe_cloudcart_agent: {e}")
        return {
            "status": "error",
            "error": f"Internal error: {str(e)}"
        }