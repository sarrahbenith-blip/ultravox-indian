"""Unit tests for cost calculator."""

import pytest

from ultravox.cost_tracking.calculator import (
    calculate_customer_cost,
    calculate_model_cost,
    calculate_stt_cost,
    calculate_tts_cost,
    calculate_total_cost,
    get_profit_margin,
)


class TestSTTCostCalculation:
    """Test STT cost calculation."""

    def test_sarvam_stt_cost(self):
        """Test Sarvam AI STT cost calculation."""
        cost = calculate_stt_cost("sarvam", audio_duration_seconds=60.0)
        # 60 seconds * $0.00006 per second = $0.0036
        assert cost == pytest.approx(0.0036, rel=1e-5)

    def test_google_stt_cost(self):
        """Test Google Cloud STT cost calculation."""
        cost = calculate_stt_cost("google", audio_duration_seconds=60.0)
        # 60 seconds * $0.0004 per second = $0.024
        assert cost == pytest.approx(0.024, rel=1e-5)

    def test_stt_cost_zero_duration(self):
        """Test STT cost with zero duration."""
        cost = calculate_stt_cost("sarvam", audio_duration_seconds=0.0)
        assert cost == 0.0

    def test_stt_cost_partial_second(self):
        """Test STT cost with fractional seconds."""
        cost = calculate_stt_cost("sarvam", audio_duration_seconds=2.5)
        expected = 2.5 * 0.00006
        assert cost == pytest.approx(expected, rel=1e-5)


class TestTTSCostCalculation:
    """Test TTS cost calculation."""

    def test_sarvam_tts_cost_by_duration(self):
        """Test Sarvam AI TTS cost by audio duration."""
        cost = calculate_tts_cost("sarvam", audio_duration_seconds=60.0)
        # 60 seconds * $0.0001 per second = $0.006
        assert cost == pytest.approx(0.006, rel=1e-5)

    def test_google_tts_cost_by_characters(self):
        """Test Google Cloud TTS cost by text length."""
        # Approximate: 1000 characters
        cost = calculate_tts_cost("google", text_length=1000)
        # 1000 characters * $0.000004 per character = $0.004
        assert cost == pytest.approx(0.004, rel=1e-5)

    def test_sarvam_tts_cost_zero(self):
        """Test Sarvam TTS cost with zero duration."""
        cost = calculate_tts_cost("sarvam", audio_duration_seconds=0.0)
        assert cost == 0.0

    def test_google_tts_cost_zero(self):
        """Test Google TTS cost with zero characters."""
        cost = calculate_tts_cost("google", text_length=0)
        assert cost == 0.0


class TestModelCostCalculation:
    """Test model inference cost calculation."""

    def test_model_cost_fixed(self):
        """Test that model cost is fixed per request."""
        cost1 = calculate_model_cost(tokens=100)
        cost2 = calculate_model_cost(tokens=1000)
        # Should be same regardless of tokens (MVP uses fixed cost)
        assert cost1 == cost2
        assert cost1 == pytest.approx(0.001, rel=1e-5)

    def test_model_cost_none_args(self):
        """Test model cost with no arguments."""
        cost = calculate_model_cost()
        assert cost == pytest.approx(0.001, rel=1e-5)


class TestTotalCostCalculation:
    """Test total cost calculation."""

    def test_total_cost(self):
        """Test total cost from components."""
        stt_cost = 0.006
        model_cost = 0.001
        tts_cost = 0.008
        total = calculate_total_cost(stt_cost, model_cost, tts_cost)
        assert total == pytest.approx(0.015, rel=1e-5)

    def test_total_cost_zero(self):
        """Test total cost with all zeros."""
        total = calculate_total_cost(0.0, 0.0, 0.0)
        assert total == 0.0


class TestCustomerCostCalculation:
    """Test customer billing cost calculation."""

    def test_basic_tier_billing(self):
        """Test basic tier pricing."""
        result = calculate_customer_cost(1.0, tier="basic")
        assert result["tier"] == "basic"
        assert result["cost_usd"] == pytest.approx(0.03, rel=1e-5)
        assert result["cost_inr"] == pytest.approx(2.50, rel=1e-5)

    def test_premium_tier_billing(self):
        """Test premium tier pricing."""
        result = calculate_customer_cost(1.0, tier="premium")
        assert result["tier"] == "premium"
        assert result["cost_usd"] == pytest.approx(0.048, rel=1e-5)
        assert result["cost_inr"] == pytest.approx(4.00, rel=1e-5)

    def test_customer_cost_multiple_minutes(self):
        """Test billing for multiple minutes."""
        result = calculate_customer_cost(60.0, tier="basic")
        expected_usd = 60.0 * 0.03
        assert result["cost_usd"] == pytest.approx(expected_usd, rel=1e-5)

    def test_customer_cost_invalid_tier(self):
        """Test invalid tier raises error."""
        with pytest.raises(ValueError):
            calculate_customer_cost(1.0, tier="invalid")


class TestProfitMarginCalculation:
    """Test profit margin calculation."""

    def test_profit_margin_basic_tier_sarvam(self):
        """Test profit margin for basic tier with Sarvam."""
        # Typical Sarvam usage per minute: 2 turns, 30s each
        # STT: 2 * 30 * 0.00006 = 0.0036
        # Model: 2 * 0.001 = 0.002
        # TTS: 2 * 30 * 0.0001 = 0.006
        # Total cost: 0.0116
        # Customer price: 0.03
        provider_cost = 0.0116
        customer_price = 0.03
        margin = get_profit_margin(provider_cost, customer_price)
        expected = ((customer_price - provider_cost) / provider_cost) * 100
        assert margin == pytest.approx(expected, rel=1e-2)

    def test_profit_margin_zero_cost(self):
        """Test profit margin with zero cost."""
        margin = get_profit_margin(0.0, 0.03)
        assert margin == 0.0

    def test_profit_margin_negative(self):
        """Test profit margin when cost exceeds price."""
        margin = get_profit_margin(1.0, 0.5)
        assert margin < 0  # Negative margin


class TestCostScenarios:
    """Test realistic cost scenarios."""

    def test_typical_1min_conversation_sarvam(self):
        """Test cost for typical 1-minute conversation with Sarvam."""
        # Typical: 3 turns, ~20 seconds each (STT + Model + TTS)
        stt_duration = 3 * 20  # seconds
        tts_duration = 3 * 15  # seconds (shorter response)
        tokens = 3 * 50

        stt_cost = calculate_stt_cost("sarvam", stt_duration)
        tts_cost = calculate_tts_cost("sarvam", tts_duration)
        model_cost = calculate_model_cost(tokens)

        total_cost = calculate_total_cost(stt_cost, model_cost, tts_cost)

        # Total should be less than $0.03 (basic tier price)
        assert total_cost < 0.03
        assert total_cost > 0.0

    def test_typical_1min_conversation_google(self):
        """Test cost for typical 1-minute conversation with Google."""
        stt_duration = 3 * 20
        text_length = 3 * 30  # approximate characters for response

        stt_cost = calculate_stt_cost("google", stt_duration)
        tts_cost = calculate_tts_cost("google", text_length=text_length)
        model_cost = calculate_model_cost()

        total_cost = calculate_total_cost(stt_cost, model_cost, tts_cost)

        # Should be less than $0.048 (premium tier price)
        assert total_cost < 0.048
        assert total_cost > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
