"""Factory functions for creating TTS provider instances."""

from typing import Any

from ultravox.providers.base import TTSProviderBase


def create_tts_provider(provider_name: str, **config: Any) -> TTSProviderBase:
    """
    Factory function to create TTS provider instances.

    Args:
        provider_name: Provider name ("sarvam", "google", etc.)
        **config: Provider-specific configuration

    Returns:
        Instantiated TTS provider

    Raises:
        ValueError: If provider_name is unknown
    """
    if provider_name == "sarvam":
        from ultravox.providers.tts.sarvam import SarvamTTSProvider

        return SarvamTTSProvider(**config)

    elif provider_name == "google":
        from ultravox.providers.tts.google import GoogleTTSProvider

        return GoogleTTSProvider(**config)

    else:
        raise ValueError(f"Unknown TTS provider: {provider_name}")
