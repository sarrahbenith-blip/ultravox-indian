"""Factory functions for creating STT provider instances."""

from typing import Any

from ultravox.providers.base import STTProviderBase


def create_stt_provider(provider_name: str, **config: Any) -> STTProviderBase:
    """
    Factory function to create STT provider instances.

    Args:
        provider_name: Provider name ("sarvam", "google", etc.)
        **config: Provider-specific configuration

    Returns:
        Instantiated STT provider

    Raises:
        ValueError: If provider_name is unknown
    """
    if provider_name == "sarvam":
        from ultravox.providers.stt.sarvam import SarvamSTTProvider

        return SarvamSTTProvider(**config)

    elif provider_name == "google":
        from ultravox.providers.stt.google import GoogleSTTProvider

        return GoogleSTTProvider(**config)

    else:
        raise ValueError(f"Unknown STT provider: {provider_name}")
