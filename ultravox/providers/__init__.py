"""
Provider abstraction layer for TTS and STT services.

This module provides a pluggable architecture for integrating multiple
TTS/STT providers (Sarvam AI, Google Cloud, etc.) with a unified interface.
"""

from ultravox.providers.base import (
    TTSProviderBase,
    STTProviderBase,
    ProviderAPIError,
    UnsupportedLanguageError,
    ProviderConfigError,
)

__all__ = [
    "TTSProviderBase",
    "STTProviderBase",
    "ProviderAPIError",
    "UnsupportedLanguageError",
    "ProviderConfigError",
]
