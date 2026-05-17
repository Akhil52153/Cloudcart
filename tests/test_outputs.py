"""Tests for output validation."""

import pytest
from src.validators.output_validator import output_validator


class TestValidOutputs:
    """Test cases for valid LLM outputs."""

    def test_helpful_response(self):
        result = output_validator("To reset your password, click the 'Forgot Password' link.")
        assert result["valid"] is True

    def test_support_info(self):
        result = output_validator("Our support hours are 9 AM to 5 PM EST.")
        assert result["valid"] is True

    def test_normal_response(self):
        result = output_validator("I'm here to help with your CloudCart account.")
        assert result["valid"] is True


class TestInvalidOutputs:
    """Test cases for invalid LLM outputs."""

    def test_prompt_leakage(self):
        result = output_validator("The system prompt says: You are a support agent...")
        assert result["valid"] is False
        assert "leakage" in result["reason"]

    def test_hallucinated_product(self):
        result = output_validator("This product costs $29.99 and is available now.")
        assert result["valid"] is False
        assert "hallucinated" in result["reason"]

    def test_out_of_scope_politics(self):
        result = output_validator("Regarding the current political situation...")
        assert result["valid"] is False
        assert "scope" in result["reason"]

    def test_out_of_scope_religion(self):
        result = output_validator("From a religious perspective...")
        assert result["valid"] is False
        assert "scope" in result["reason"]