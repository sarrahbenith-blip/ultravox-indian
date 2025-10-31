"""
Cost calculation module for provider usage and customer billing.
"""

import os
from typing import Any, Dict

# Provider cost rates (USD per unit)
PROVIDER_COSTS = {
    "sarvam": {
        "stt_per_second": float(os.getenv("SARVAM_STT_COST_PER_SECOND", "0.00006")),
        "tts_per_second": float(os.getenv("SARVAM_TTS_COST_PER_SECOND", "0.0001")),
    },
    "google": {
        "stt_per_second": float(os.getenv("GOOGLE_STT_COST_PER_SECOND", "0.0004")),
        "tts_per_character": float(os.getenv("GOOGLE_TTS_COST_PER_CHARACTER", "0.000004")),
    },
}

# Model inference cost
MODEL_INFERENCE_COST_PER_REQUEST = float(
    os.getenv("ULTRAVOX_INFERENCE_COST_PER_REQUEST", "0.001")
)

# Customer pricing tiers
PRICING_TIERS = {
    "basic": {
        "per_minute_usd": float(os.getenv("BASIC_TIER_PRICE_USD", "0.03")),
        "per_minute_inr": float(os.getenv("BASIC_TIER_PRICE_INR", "2.50")),
        "allowed_providers": ["sarvam"],
    },
    "premium": {
        "per_minute_usd": float(os.getenv("PREMIUM_TIER_PRICE_USD", "0.048")),
        "per_minute_inr": float(os.getenv("PREMIUM_TIER_PRICE_INR", "4.00")),
        "allowed_providers": ["sarvam", "google"],
    },
}

# INR to USD conversion rate
USD_TO_INR = 83.0  # Approximate


def calculate_stt_cost(provider: str, audio_duration_seconds: float) -> float:
    """
    Calculate STT cost based on provider and audio duration.

    Args:
        provider: Provider name ("sarvam", "google")
        audio_duration_seconds: Audio duration in seconds

    Returns:
        Cost in USD
    """
    if provider not in PROVIDER_COSTS:
        return 0.0

    cost_per_second = PROVIDER_COSTS[provider].get("stt_per_second", 0.0)
    return audio_duration_seconds * cost_per_second


def calculate_tts_cost(
    provider: str,
    audio_duration_seconds: float = None,
    text_length: int = None,
) -> float:
    """
    Calculate TTS cost based on provider and either audio duration or text length.

    Args:
        provider: Provider name ("sarvam", "google")
        audio_duration_seconds: Generated audio duration (for Sarvam)
        text_length: Character count (for Google Cloud)

    Returns:
        Cost in USD
    """
    if provider not in PROVIDER_COSTS:
        return 0.0

    if provider == "sarvam" and audio_duration_seconds is not None:
        cost_per_second = PROVIDER_COSTS[provider].get("tts_per_second", 0.0)
        return audio_duration_seconds * cost_per_second

    elif provider == "google" and text_length is not None:
        cost_per_char = PROVIDER_COSTS[provider].get("tts_per_character", 0.0)
        return text_length * cost_per_char

    return 0.0


def calculate_model_cost(
    tokens: int = None,
    inference_time: float = None,
) -> float:
    """
    Calculate Ultravox model inference cost.

    Args:
        tokens: Total tokens (input + output), currently unused
        inference_time: Inference time in seconds, currently unused

    Returns:
        Cost in USD (fixed per inference for MVP)
    """
    return MODEL_INFERENCE_COST_PER_REQUEST


def calculate_total_cost(stt_cost: float, model_cost: float, tts_cost: float) -> float:
    """
    Calculate total cost from component costs.

    Args:
        stt_cost: STT provider cost in USD
        model_cost: Model inference cost in USD
        tts_cost: TTS provider cost in USD

    Returns:
        Total cost in USD
    """
    return stt_cost + model_cost + tts_cost


def calculate_customer_cost(
    conversation_duration_minutes: float,
    tier: str = "basic",
) -> Dict[str, Any]:
    """
    Calculate customer billing amount.

    Args:
        conversation_duration_minutes: Total conversation duration
        tier: Pricing tier ("basic" or "premium")

    Returns:
        Dict with:
            - cost_usd: Cost in USD
            - cost_inr: Cost in INR
            - tier: Pricing tier used
            - per_minute_usd: Price per minute
            - per_minute_inr: Price per minute in INR

    Raises:
        ValueError: If tier is invalid
    """
    if tier not in PRICING_TIERS:
        raise ValueError(f"Unknown pricing tier: {tier}")

    tier_config = PRICING_TIERS[tier]
    per_minute_usd = tier_config["per_minute_usd"]
    per_minute_inr = tier_config["per_minute_inr"]

    cost_usd = conversation_duration_minutes * per_minute_usd
    cost_inr = conversation_duration_minutes * per_minute_inr

    return {
        "cost_usd": round(cost_usd, 4),
        "cost_inr": round(cost_inr, 2),
        "tier": tier,
        "per_minute_usd": per_minute_usd,
        "per_minute_inr": per_minute_inr,
        "duration_minutes": conversation_duration_minutes,
    }


def get_profit_margin(
    provider_cost_usd: float,
    customer_price_usd: float,
) -> float:
    """
    Calculate profit margin percentage.

    Args:
        provider_cost_usd: Total provider cost in USD
        customer_price_usd: Customer billing price in USD

    Returns:
        Profit margin as percentage (0-100)
    """
    if provider_cost_usd == 0:
        return 0.0

    profit = customer_price_usd - provider_cost_usd
    return (profit / provider_cost_usd) * 100
